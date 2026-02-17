from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities import Directory, DirectoryId
from application.exceptions import DirectoryAlreadyExistsError, DirectoryNotFoundError
from infrastructure.adapters.mappers import SqlAlchemyDirectoryMapper
from infrastructure.exceptions.error_aware_decorators import network_error_aware
from infrastructure.exceptions.asyncpg_unique_error_handler import (
    unique_violation_aware,
)
from infrastructure.models import ProjectUnitNode


class SqlAlchemyDirectoryCommandGateway:

    def __init__(self, mapper: SqlAlchemyDirectoryMapper, session: AsyncSession):
        self._mapper: SqlAlchemyDirectoryMapper = mapper
        self._session: AsyncSession = session

    @network_error_aware("Cannot add directory: directories are unavailable")
    @unique_violation_aware(
        DirectoryAlreadyExistsError(
            "Directory with the same name and parent_directory already exsists"
        )
    )
    async def add(self, directory: Directory) -> None:

        node: ProjectUnitNode = self._mapper.to_dto(directory)
        self._session.add(node)
        await self._session.flush()


class SqlAlchemyDirectoryQueryGateway:

    def __init__(self, mapper: SqlAlchemyDirectoryMapper, session: AsyncSession):
        self._mapper: SqlAlchemyDirectoryMapper = mapper
        self._session: AsyncSession = session

    @network_error_aware("Cannot find directory: directories are unavailable")
    async def by_id(self, directory_id: DirectoryId) -> Directory:

        stmt = select(ProjectUnitNode).where(ProjectUnitNode.id_ == directory_id)
        node: ProjectUnitNode | None = (
            await self._session.execute(stmt)
        ).scalar_one_or_none()

        if not node:
            raise DirectoryNotFoundError("Directory with given id does not exists")

        return self._mapper.to_domain(node)
