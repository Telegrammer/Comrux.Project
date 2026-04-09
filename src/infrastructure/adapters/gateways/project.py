from typing import Sequence
from functools import singledispatchmethod


from sqlalchemy import select, Select, delete as sql_delete, Delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import UUID


from domain import Project, ProjectId, UserId
from domain.enums import ProjectRole
from application.exceptions import (
    ProjectAlreadyExistsError,
    ProjectNotFoundError,
)
from application.ports.gateways.query_params import ProjectListParams
from infrastructure.models import Project as OrmProject
from infrastructure.exceptions import (
    unique_violation_aware,
    network_error_aware,
    stale_data_error_aware,
)
from infrastructure.adapters.mappers import SqlAlchemyProjectMapper
from infrastructure.models import ProjectMembership, ProjectDto, ProjectUnitNode
from .query_builder import SQLAlchemyQueryBuilder


class SqlAlchemyProjectCommandGateway:
    def __init__(self, session: AsyncSession, mapper: SqlAlchemyProjectMapper):
        self._session: AsyncSession = session
        self._mapper: SqlAlchemyProjectMapper = mapper

    @unique_violation_aware(
        ProjectAlreadyExistsError("Project with the same data already exists")
    )
    @network_error_aware("Cannot add project: there is no place to add him via network")
    async def add(self, project: Project):
        orm_project: OrmProject = self._mapper.to_dto(project).orm_model
        self._session.add(orm_project)
        await self._session.flush()

    @stale_data_error_aware("Application and database project are different")
    @network_error_aware("Cannot update project: project are unreachable via network")
    async def update(self, project: Project) -> None:
        old_dto: OrmProject = await self._session.get(OrmProject, project.id_)
        orm_project: OrmProject = self._mapper.to_dto(project, old_dto).orm_model
        await self._session.merge(orm_project)
        await self._session.flush()

    @singledispatchmethod
    async def delete(self, obj) -> None:
        raise NotImplementedError

    @network_error_aware("Cannot delete project: project are unreachable via network")
    @delete.register(Project)
    async def _(self, obj: Project) -> None:
        persisted: OrmProject = await self._session.get(OrmProject, obj.id_)
        await self._session.delete(persisted)

    @network_error_aware("Cannot delete project: project are unreachable via network")
    @delete.register(ProjectId)
    async def _(self, obj: ProjectId):
        stmt: Delete = sql_delete(OrmProject).where(OrmProject.id_ == obj)
        await self._session.execute(stmt)


class SqlAlchemyProjectQueryGateway:
    def __init__(
        self,
        session: AsyncSession,
        mapper: SqlAlchemyProjectMapper,
        query_builder: SQLAlchemyQueryBuilder,
    ):
        self._session: AsyncSession = session
        self._mapper: SqlAlchemyProjectMapper = mapper
        self._query_builder: SQLAlchemyQueryBuilder = query_builder

    @network_error_aware("Cannot get projects: projects are unreachable via network")
    async def read_all(self, params: ProjectListParams) -> Sequence[Project]:
        stmt = (
            select(OrmProject, ProjectUnitNode.id_)
            .join(ProjectUnitNode, ProjectUnitNode.project_id == OrmProject.id_)
            .where(ProjectUnitNode.parent_id.is_(None))
        )

        stmt = self._query_builder.apply(stmt, params, OrmProject)

        response: Sequence[tuple[OrmProject, UUID]] = (
            await self._session.execute(stmt)
        ).all()

        return [
            self._mapper.to_domain(ProjectDto(proj, root_id))
            for proj, root_id in response
        ]

    @network_error_aware("Cannot get project: project are unreachable via network")
    async def by_id(self, project_id: ProjectId) -> Project:

        stmt = (
            select(OrmProject, ProjectUnitNode.id_)
            .join(ProjectUnitNode, ProjectUnitNode.project_id == OrmProject.id_)
            .where(OrmProject.id_ == project_id)
            .where(ProjectUnitNode.parent_id.is_(None))
        )

        response: tuple[OrmProject, UUID] = (
            await self._session.execute(stmt)
        ).one_or_none()

        if not response:
            raise ProjectNotFoundError("Project with given id does not exists")

        project, root_id = response

        return self._mapper.to_domain(ProjectDto(project, root_id))

    @network_error_aware("Cannot get projects: projects are unreachable via network")
    async def by_user(
        self, user_id: UserId, role: ProjectRole, params: ProjectListParams
    ) -> Sequence[tuple[Project, ProjectRole]]:

        stmt: Select = (
            select(
                OrmProject,
                ProjectUnitNode.id_,
                ProjectMembership.role.label("member_role"),
            )
            .join(ProjectMembership, ProjectMembership.project_id == OrmProject.id_)
            .join(ProjectUnitNode, ProjectUnitNode.project_id == OrmProject.id_)
            .where(ProjectUnitNode.parent_id.is_(None))
            .where(ProjectMembership.user_id == user_id)
        )

        if role:
            stmt = stmt.where(ProjectMembership.role == role)

        stmt = self._query_builder.apply(stmt, params, OrmProject)
        response: Sequence[tuple[OrmProject, UUID, ProjectRole]] = (
            await self._session.execute(stmt)
        ).all()
        return [
            (self._mapper.to_domain(ProjectDto(proj, root_id)), role)
            for proj, root_id, role in response
        ]
