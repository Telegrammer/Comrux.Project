from typing import Sequence

from sqlalchemy import select, delete as sql_delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload, selectin_polymorphic

from domain.value_objects import Name
from domain.entities import AccessList, ProjectId, AccessListId
from application.models import ProjectAccessListsRead
from application.ports.gateways.query_params import AccessListsParams
from application.exceptions.access_list import (
    AccessListAlreadyExistsError,
    AccessListNotFoundError,
)
from infrastructure.models import (
    AccessList as OrmAccessList,
    User as OrmUser,
    AccessRule as OrmAccessRule,
    AccessRuleUserTarget,
    AccessRuleRoleTarget,
    AccessRuleTarget,
)
from infrastructure.adapters.mappers import SqlAlchemyAccessListMapper
from infrastructure.exceptions.error_aware_decorators import network_error_aware
from infrastructure.exceptions.asyncpg_unique_error_handler import (
    unique_violation_aware,
)
from infrastructure.adapters.access_rule_target_collector import (
    SqlAlchemyAccessRuleTargetCollector,
)
from infrastructure.adapters.gateways import SQLAlchemyQueryBuilder


import logging

logging.getLogger("sqlalchemy.engine").setLevel(logging.DEBUG)


class SqlAlchemyAccessListCommandGateway:

    def __init__(
        self,
        session: AsyncSession,
        mapper: SqlAlchemyAccessListMapper,
    ):
        self._session = session
        self._mapper = mapper

    @network_error_aware("Cannot add access list: lists are unavailable")
    @unique_violation_aware(
        AccessListAlreadyExistsError(
            "Access list with the same name already exists in project"
        )
    )
    async def add(self, access_list: AccessList) -> None:
        collector = SqlAlchemyAccessRuleTargetCollector()
        for rule in access_list.rules:
            rule.target.accept(collector)

        await collector.persist_targets(self._session)
        dto: OrmAccessList = self._mapper.to_dto(access_list, collector)

        self._session.add(dto)
        await self._session.flush()

    @network_error_aware("Cannot delet access list: there is no access list available")
    async def delete(self, access_list: AccessList) -> None:
        await self._session.execute(
            sql_delete(OrmAccessList).where(OrmAccessList.id_ == access_list.id_)
        )


class SqlAlchemyAccessListQueryGateway:

    def __init__(
        self,
        session: AsyncSession,
        mapper: SqlAlchemyAccessListMapper,
        query_builder: SQLAlchemyQueryBuilder,
    ):
        self._session = session
        self._mapper = mapper
        self._query_builder = query_builder

    @network_error_aware("Cannot find access lists, because they are unreachable")
    async def by_project(
        self, project_id: ProjectId, params: AccessListsParams
    ) -> ProjectAccessListsRead:

        stmt = (
            select(OrmAccessList, OrmUser.name)
            .join(OrmUser, OrmUser.id_ == OrmAccessList.owner)
            .where(OrmAccessList.project_id == project_id)
            .options(
                selectinload(OrmAccessList.rules)
                .selectinload(OrmAccessRule.target)
                .selectin_polymorphic([AccessRuleUserTarget, AccessRuleRoleTarget]),
                selectinload(OrmAccessList.rules)
                .selectinload(OrmAccessRule.target.of_type(AccessRuleUserTarget))
                .joinedload(AccessRuleUserTarget.user)
                .load_only(OrmUser.name),
            )
        )
        stmt = self._query_builder.apply(stmt, params, model=OrmAccessList)
        response: Sequence[tuple[OrmAccessList, str]] = (
            await self._session.execute(stmt)
        ).all()

        return self._mapper.to_list_model(response)

    @network_error_aware("Cannot find access lists, because they are unreachable")
    async def by_id(self, access_list_id: AccessListId) -> AccessList:
        stmt = select(OrmAccessList).where(OrmAccessList.id_ == access_list_id)

        response: OrmAccessList | None = (
            await self._session.execute(stmt)
        ).scalar_one_or_none()

        if not response:
            raise AccessListNotFoundError("Access list with given id does not exists")

        return self._mapper.to_domain(response)
