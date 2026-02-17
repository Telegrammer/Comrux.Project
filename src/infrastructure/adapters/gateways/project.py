__all__ = ["SqlAlchemyProjectCommandGateway", "SqlAlchemyProjectQueryGateway"]


from typing import Sequence
from functools import singledispatchmethod


from sqlalchemy import select, Select, delete as sql_delete, Delete, or_
from sqlalchemy.ext.asyncio import AsyncSession


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
from infrastructure.models import ProjectMembership
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
        orm_project: OrmProject = self._mapper.to_dto(project)
        self._session.add(orm_project)
        await self._session.flush()

    @stale_data_error_aware("Application and database project are different")
    @network_error_aware("Cannot update project: project are unreachable via network")
    async def update(self, project: Project) -> None:
        old_dto: OrmProject = await self._session.get(OrmProject, project.id_)
        orm_project: OrmProject = self._mapper.to_dto(project, old_dto)
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

        stmt: Select = self._query_builder.apply(select(OrmProject), params, OrmProject)

        response = await self._session.scalars(stmt)
        projects: Sequence[OrmProject] = response.all()
        return [self._mapper.to_domain(proj) for proj in projects]

    @network_error_aware("Cannot get project: project are unreachable via network")
    async def by_id(self, project_id: ProjectId) -> Project:

        stmt = select(OrmProject).where(OrmProject.id_ == project_id)
        response = await self._session.execute(stmt)
        project = response.scalar_one_or_none()

        if not project:
            raise ProjectNotFoundError("Project with given id does not exists")

        return self._mapper.to_domain(project)

    @network_error_aware("Cannot get projects: projects are unreachable via network")
    async def by_user(
        self, user_id: UserId, role: ProjectRole, params: ProjectListParams
    ) -> Sequence[tuple[Project, ProjectRole]]:

        stmt = (
            select(
                OrmProject,
                ProjectMembership.role.label("member_role"),
            )
            .join(ProjectMembership, ProjectMembership.project_id == OrmProject.id_)
            .where(ProjectMembership.user_id == user_id)
            .where(or_(role is None, ProjectMembership.role == role))
        )
        stmt = self._query_builder.apply(stmt, params, OrmProject)
        response: Sequence[tuple[OrmProject, ProjectRole]] = (
            await self._session.execute(stmt)
        ).all()
        return [(self._mapper.to_domain(proj), role) for proj, role in response]
