__all__ = ["SqlAlchemyProjectCommandGateway", "SqlAlchemyProjectQueryGateway"]


from typing import Sequence


from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, InterfaceError
from asyncpg.exceptions import UniqueViolationError


from domain import Project, ProjectId

from application.exceptions import ProjectAlreadyExistsError, ProjectNotFoundError
from application.ports.gateways.errors import GatewayFailedError
from application.ports.gateways.query_params import ProjectListParams
from infrastructure.models import Project as OrmProject
from infrastructure.exceptions.common import create_error_aware_decorator
from infrastructure.adapters.mappers import SqlAlchemyProjectMapper


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

    @network_error_aware("Cannot add project: projects are unreachable via network")
    async def add(self, project: Project):
        try:
            orm_user: OrmProject = self._mapper.to_dto(project)
            self._session.add(orm_user)
            await self._session.flush()
        except IntegrityError as e:
            original_error = e.orig
            if (
                getattr(original_error, "sqlstate", None)
                != UniqueViolationError.sqlstate
            ):
                raise

            error_detail: str = str(original_error).split("\n")[1]
            if error_detail.startswith("DETAIL:  Key (id_)"):
                raise GatewayFailedError(
                    "Somehow user was created with the same id. Please try again"
                )

            raise ProjectAlreadyExistsError("Project with the same data already exists")


class SqlAlchemyProjectQueryGateway:

    def __init__(self, session: AsyncSession, mapper: SqlAlchemyProjectMapper):
        self._session: AsyncSession = session
        self._mapper: SqlAlchemyProjectMapper = mapper

    @network_error_aware("Cannot get projects: projects are unreachable via network")
    async def read_all(self, params: ProjectListParams) -> Sequence[Project]:

        search = self._mapper.generate_search_params(params, OrmProject)

        stmt = select(OrmProject)

        if search.orders:
            stmt = stmt.order_by(*search.orders)

        stmt = stmt.slice(params.pagination.offset, params.pagination.limit)

        response = await self._session.scalars(stmt)
        projects: Sequence[OrmProject] = response.all()
        return [self._mapper.to_domain(proj) for proj in projects]
