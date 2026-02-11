__all__ = ["SqlAlchemyProjectCommandGateway", "SqlAlchemyProjectQueryGateway"]


from typing import Sequence
from functools import singledispatchmethod


from sqlalchemy import select, Select, delete as sql_delete, Delete, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import InterfaceError
from sqlalchemy.orm.exc import StaleDataError


from domain import Project, ProjectId, UserId
from domain.enums import ProjectRole
from application.exceptions import (
    ProjectAlreadyExistsError,
    ProjectNotFoundError,
    InconsistentDataError,
)
from application.ports.gateways.errors import GatewayFailedError
from application.ports.gateways.query_params import ProjectListParams
from infrastructure.models import Project as OrmProject
from infrastructure.exceptions import (
    create_error_aware_decorator,
    unique_violation_aware,
)
from infrastructure.adapters.mappers import SqlAlchemyProjectMapper
from infrastructure.models.search_params import SqlAlchemySearchParams
from infrastructure.models import ProjectMembership

network_error_aware = create_error_aware_decorator(
    {
        frozenset(
            {ConnectionRefusedError, ConnectionResetError, InterfaceError}
        ): GatewayFailedError
    }
)
stale_data_error_aware = create_error_aware_decorator(
    {frozenset({StaleDataError}): InconsistentDataError}
)


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

    def __init__(self, session: AsyncSession, mapper: SqlAlchemyProjectMapper):
        self._session: AsyncSession = session
        self._mapper: SqlAlchemyProjectMapper = mapper

    @network_error_aware("Cannot get projects: projects are unreachable via network")
    async def read_all(self, params: ProjectListParams) -> Sequence[Project]:

        search: SqlAlchemySearchParams = self._mapper.generate_search_params(
            params, OrmProject
        )

        stmt: Select = (
            select(OrmProject)
            .order_by(*search.orders)
            .slice(
                params.pagination.offset,
                params.pagination.offset + params.pagination.limit,
            )
        )

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

        search = self._mapper.generate_search_params(params, OrmProject)
        stmt = (
            select(
                OrmProject,
                ProjectMembership.role.label("member_role"),
            )
            .join(ProjectMembership, ProjectMembership.project_id == OrmProject.id_)
            .where(ProjectMembership.user_id == user_id)
            .where(or_(role is None, ProjectMembership.role == role))
        )
        stmt = stmt.order_by(*search.orders).slice(
            params.pagination.offset, params.pagination.offset + params.pagination.limit
        )
        response: Sequence[tuple[OrmProject, ProjectRole]] = (
            await self._session.execute(stmt)
        ).all()
        return [(self._mapper.to_domain(proj), role) for proj, role in response]
