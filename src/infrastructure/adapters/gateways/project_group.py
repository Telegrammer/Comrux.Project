from typing import Sequence

from sqlalchemy import select, delete as sql_delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from domain.entities import ProjectGroup, ProjectGroupId, ProjectId, UserId

from application.exceptions import (
    ProjectGroupAlreadyExistsError,
    ProjectGroupNotFoundError,
)
from application.ports.gateways.query_params import ProjectGroupListParams
from infrastructure.adapters.mappers import SqlAlchemyProjectGroupMapper
from infrastructure.exceptions import network_error_aware, unique_violation_aware
from infrastructure.models import ProjectGroup as OrmProjectGroup
from infrastructure.models import ProjectGroupParticipant as OrmProjectGroupParticipant
from .query_builder import SQLAlchemyQueryBuilder


class SqlAlchemyProjectGroupCommandGateway:
    def __init__(
        self,
        session: AsyncSession,
        mapper: SqlAlchemyProjectGroupMapper,
    ) -> None:
        self._session = session
        self._mapper = mapper

    @network_error_aware("Cannot add group: groups are unavailable")
    @unique_violation_aware(
        ProjectGroupAlreadyExistsError(
            "Project group with the same name already exists in project"
        )
    )
    async def add(self, group: ProjectGroup) -> None:
        self._session.add(self._mapper.to_dto(group))
        await self._session.flush()

    @network_error_aware("Cannot update group: groups are unavailable")
    async def update(self, group: ProjectGroup) -> None:
        await self._session.merge(self._mapper.to_dto(group))
        await self._session.flush()

    @network_error_aware("Cannot delete group: groups are unavailable")
    async def delete(self, group: ProjectGroup) -> None:
        await self._session.execute(
            sql_delete(OrmProjectGroup).where(OrmProjectGroup.id_ == group.id_)
        )


class SqlAlchemyProjectGroupQueryGateway:
    def __init__(
        self,
        session: AsyncSession,
        mapper: SqlAlchemyProjectGroupMapper,
        query_builder: SQLAlchemyQueryBuilder,
    ) -> None:
        self._session = session
        self._mapper = mapper
        self._query_builder = query_builder

    @network_error_aware("Cannot find group: groups are unavailable")
    async def by_id(self, group_id: ProjectGroupId) -> ProjectGroup:
        stmt = (
            select(OrmProjectGroup)
            .where(OrmProjectGroup.id_ == group_id)
            .options(selectinload(OrmProjectGroup.participants))
        )
        dto = (await self._session.execute(stmt)).scalar_one_or_none()
        if not dto:
            raise ProjectGroupNotFoundError("Project group with given id does not exist")
        return self._mapper.to_domain(dto)

    @network_error_aware("Cannot list groups: groups are unavailable")
    async def by_project(
        self, project_id: ProjectId, params: ProjectGroupListParams
    ) -> Sequence[ProjectGroup]:
        stmt = (
            select(OrmProjectGroup)
            .where(OrmProjectGroup.project_id == project_id)
            .options(selectinload(OrmProjectGroup.participants))
        )
        stmt = self._query_builder.apply(stmt, params, OrmProjectGroup)
        response = (await self._session.execute(stmt)).scalars().all()
        return [self._mapper.to_domain(item) for item in response]

    @network_error_aware("Cannot load user project groups: groups are unavailable")
    async def group_ids_for_user(
        self, project_id: ProjectId, user_id: UserId
    ) -> frozenset[ProjectGroupId]:
        stmt = (
            select(OrmProjectGroup.id_)
            .join(
                OrmProjectGroupParticipant,
                OrmProjectGroupParticipant.group_id == OrmProjectGroup.id_,
            )
            .where(
                OrmProjectGroup.project_id == project_id,
                OrmProjectGroupParticipant.user_id == user_id,
            )
        )
        group_ids = (await self._session.execute(stmt)).scalars().all()
        return frozenset(ProjectGroupId(str(group_id)) for group_id in group_ids)
