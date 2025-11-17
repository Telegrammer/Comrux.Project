__all__ = ["SqlAlchemyProjectCommandGateway", "SqlAlchemyProjectQueryGateway"]


from typing import Sequence
from functools import singledispatchmethod


from sqlalchemy import (
    select,
    Select,
    delete as sql_delete,
    Delete,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, InterfaceError


from domain import Project, ProjectId

from application.exceptions import ProjectAlreadyExistsError, ProjectNotFoundError
from application.ports.gateways import (
    ProjectCommandGateway,
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


network_error_aware = create_error_aware_decorator(
    {
        frozenset(
            {ConnectionRefusedError, ConnectionResetError, InterfaceError}
        ): GatewayFailedError
    }
)


class SqlAlchemyProjectCommandGateway:

    def __init__(self, session: AsyncSession, mapper: SqlAlchemyProjectMapper):
        self._session: AsyncSession = session
        self._mapper: SqlAlchemyProjectMapper = mapper

    @network_error_aware("Cannot add project: there is no place to add him via network")
    @unique_violation_aware(
        ProjectAlreadyExistsError("Project with the same data already exists")
    )
    async def add(self, project: Project):
        orm_project: OrmProject = self._mapper.to_dto(project)
        self._session.add(orm_project)
        await self._session.flush()

    @network_error_aware("Cannot update project: project are unreachable via network")
    async def update(self, project: Project) -> None:
        orm_project: OrmProject = self._mapper.to_dto(project)
        await self._session.merge(orm_project)

    @singledispatchmethod
    async def delete(obj) -> None:
        raise NotImplementedError

    @network_error_aware("Cannot delete project: project are unreachable via network")
    @delete.register(Project)
    async def _(self, obj: Project) -> None:
        orm_project: OrmProject = self._mapper.to_dto(obj)
        persisted: OrmProject = await self._session.merge(orm_project)
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

        stmt: Select = select(OrmProject)

        if search.orders:
            stmt = stmt.order_by(*search.orders)

        stmt = stmt.slice(
            params.pagination.offset, params.pagination.offset + params.pagination.limit
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
