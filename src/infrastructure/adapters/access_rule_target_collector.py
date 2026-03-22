from typing import Type
from functools import singledispatchmethod
from uuid import UUID

from sqlalchemy import insert, select, Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from domain.entities.access_list import (
    AccessRuleUserTarget,
    AccessRuleRoleTarget,
    AccessRuleTargetVisior,
)
from domain.enums import ProjectRole

from infrastructure.models import (
    AccessRuleTarget,
    TargetValueMixin as OrmRuleTarget,
    AccessRuleUserTarget as OrmUserTarget,
    AccessRuleRoleTarget as OrmRoleTarget,
)


class SqlAlchemyAccessRuleTargetCollector(AccessRuleTargetVisior):

    def __init__(self) -> None:
        self._roles_ids: dict[ProjectRole, int] = {}
        self._seen_roles: set[ProjectRole] = set()

        self._users_ids: dict[UUID, int] = {}
        self._seen_users: set[UUID] = set()

    @singledispatchmethod
    def resolve(self, target) -> int:
        raise TypeError(f"Unsupported target type: {type(target)!r}")

    @resolve.register
    def _(self, target: AccessRuleRoleTarget) -> int:
        return self._roles_ids[target.role]

    @resolve.register
    def _(self, target: AccessRuleUserTarget) -> int:
        return self._users_ids[target.user_id.value]

    def visit_role(self, target: AccessRuleRoleTarget) -> None:
        self._seen_roles.add(target.role)

    def visit_user(self, target: AccessRuleUserTarget) -> None:
        self._seen_users.add(target.user_id.value)

    @staticmethod
    async def _select_existing[valT, ormT: OrmRuleTarget[valT]](
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
        target_type: str,
        count: int,
    ) -> list[int]:
        stmt = (
            insert(AccessRuleTarget)
            .values([{"type_": target_type} for _ in range(count)])
            .returning(AccessRuleTarget.id_)
        )
        return [row.id_ for row in (await session.execute(stmt)).all()]

    @staticmethod
    async def _insert_missing[valT, ormT: OrmRuleTarget[valT]](
        session: AsyncSession,
        model: Type[ormT],
        value_column: InstrumentedAttribute[valT],
        values: list[valT],
    ) -> dict[valT, int]:
        root_ids = await SqlAlchemyAccessRuleTargetCollector._insert_roots(
            session,
            str(value_column.key),
            len(values),
        )

        child_data = [
            {model.id_.key: root_id, value_column.key: value}
            for root_id, value in zip(root_ids, values, strict=True)
        ]

        await session.execute(insert(model), child_data)

        return {value: root_id for root_id, value in zip(root_ids, values, strict=True)}

    async def define_target_group[valT, ormT: OrmRuleTarget[valT]](
        self,
        session: AsyncSession,
        model: Type[ormT],
        value_attr: InstrumentedAttribute[valT],
        targets_values: set[valT],
    ) -> dict[valT, int]:
        if not targets_values:
            return {}

        values = list(targets_values)

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

    async def persist_targets(self, session: AsyncSession) -> None:
        self._roles_ids = await self.define_target_group(
            session=session,
            model=OrmRoleTarget,
            value_attr=OrmRoleTarget.role,
            targets_values=self._seen_roles,
        )

        self._users_ids = await self.define_target_group(
            session=session,
            model=OrmUserTarget,
            value_attr=OrmUserTarget.user_id,
            targets_values=self._seen_users,
        )
