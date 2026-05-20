from functools import singledispatchmethod
from typing import Type
from uuid import UUID

from sqlalchemy import Select, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from domain.entities import (
    AccessRuleGroupResponsible,
    AccessRuleRoleResponsible,
    AccessRuleResponsibleVisitor,
    AccessRuleUserResponsible,
)
from domain.enums import ProjectRole
from infrastructure.models import (
    Responsible as OrmResponsible,
    GroupResponsible as OrmGroupResponsible,
    RoleResponsible as OrmRoleResponsible,
    UserResponsible as OrmUserResponsible,
    ResponsibleValueMixin as OrmResponsibleValue,
)


class SqlAlchemyResponsibleCollector(AccessRuleResponsibleVisitor):
    def __init__(self) -> None:
        self._roles_ids: dict[ProjectRole, int] = {}
        self._seen_roles: set[ProjectRole] = set()
        self._users_ids: dict[UUID, int] = {}
        self._seen_users: set[UUID] = set()
        self._groups_ids: dict[UUID, int] = {}
        self._seen_groups: set[UUID] = set()

    @singledispatchmethod
    def resolve(self, responsible) -> int:
        raise TypeError(f"Unsupported responsible type: {type(responsible)!r}")

    @resolve.register
    def _(self, responsible: AccessRuleRoleResponsible) -> int:
        return self._roles_ids[responsible.role]

    @resolve.register
    def _(self, responsible: AccessRuleUserResponsible) -> int:
        return self._users_ids[UUID(responsible.user_id.value)]

    @resolve.register
    def _(self, responsible: AccessRuleGroupResponsible) -> int:
        return self._groups_ids[UUID(responsible.group_id.value)]

    def visit_role(self, responsible: AccessRuleRoleResponsible) -> None:
        self._seen_roles.add(responsible.role)

    def visit_user(self, responsible: AccessRuleUserResponsible) -> None:
        self._seen_users.add(UUID(responsible.user_id.value))

    def visit_group(self, responsible: AccessRuleGroupResponsible) -> None:
        self._seen_groups.add(UUID(responsible.group_id.value))

    def collect(self, responsible) -> None:
        responsible.accept(self)

    @staticmethod
    async def _select_existing[valT, ormT: OrmResponsibleValue[valT]](
        session: AsyncSession,
        model: Type[ormT],
        value_column: InstrumentedAttribute[valT],
        values: list[valT],
    ) -> dict[valT, int]:
        stmt: Select = select(model.id_, value_column).where(value_column.in_(values))
        return {value: fk_id for fk_id, value in (await session.execute(stmt)).all()}

    @staticmethod
    async def _insert_roots(
        session: AsyncSession,
        responsible_type: str,
        count: int,
    ) -> list[int]:
        stmt = (
            insert(OrmResponsible)
            .values([{"type_": responsible_type} for _ in range(count)])
            .returning(OrmResponsible.id_)
        )
        return [row.id_ for row in (await session.execute(stmt)).all()]

    @staticmethod
    async def _insert_missing[valT, ormT: OrmResponsibleValue[valT]](
        session: AsyncSession,
        model: Type[ormT],
        value_column: InstrumentedAttribute[valT],
        values: list[valT],
    ) -> dict[valT, int]:
        polymorphic_identity = str(model.__mapper__.polymorphic_identity)
        root_ids = await SqlAlchemyResponsibleCollector._insert_roots(
            session=session,
            responsible_type=polymorphic_identity,
            count=len(values),
        )
        rows = [
            {model.id_.key: root_id, value_column.key: value}
            for root_id, value in zip(root_ids, values, strict=True)
        ]
        await session.execute(insert(model.__table__), rows)
        return {value: root_id for root_id, value in zip(root_ids, values, strict=True)}

    async def _define_responsible_group[valT, ormT: OrmResponsibleValue[valT]](
        self,
        session: AsyncSession,
        model: Type[ormT],
        value_attr: InstrumentedAttribute[valT],
        values_set: set[valT],
    ) -> dict[valT, int]:
        if not values_set:
            return {}
        values = list(values_set)
        existing = await self._select_existing(
            session=session,
            model=model,
            value_column=value_attr,
            values=values,
        )
        missing_values = [value for value in values if value not in existing]
        created: dict[valT, int] = {}
        if missing_values:
            created = await self._insert_missing(
                session=session,
                model=model,
                value_column=value_attr,
                values=missing_values,
            )
        existing.update(created)
        return existing

    async def persist_responsibles(self, session: AsyncSession) -> None:
        self._roles_ids = await self._define_responsible_group(
            session=session,
            model=OrmRoleResponsible,
            value_attr=OrmRoleResponsible.role,
            values_set=self._seen_roles,
        )
        self._users_ids = await self._define_responsible_group(
            session=session,
            model=OrmUserResponsible,
            value_attr=OrmUserResponsible.user_id,
            values_set=self._seen_users,
        )
        self._groups_ids = await self._define_responsible_group(
            session=session,
            model=OrmGroupResponsible,
            value_attr=OrmGroupResponsible.group_id,
            values_set=self._seen_groups,
        )
