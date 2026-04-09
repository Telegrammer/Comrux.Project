from sqlalchemy import select, delete as sql_delete
from sqlalchemy.orm import aliased
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities import Directory, DirectoryId
from application.exceptions import DirectoryAlreadyExistsError, DirectoryNotFoundError
from domain.entities.document import ContentId
from domain.enums.project_unit_type import ProjectUnitType
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

    @network_error_aware("Cannot delete document: document are unreachable via network")
    async def delete(self, directory_id: DirectoryId) -> list[ContentId]:

        tree = (
            select(ProjectUnitNode.id_)
            .where(ProjectUnitNode.id_ == directory_id)
            .cte("tree", recursive=True)
        )

        pun = aliased(ProjectUnitNode)
        tree = tree.union_all(select(pun.id_).where(pun.parent_id == tree.c.id_))

        stmt = (
            sql_delete(ProjectUnitNode)
            .where(ProjectUnitNode.id_.in_(select(tree.c.id_)))
            .returning(ProjectUnitNode.attributes, ProjectUnitNode.unit_type)
        )

        response = (await self._session.execute(stmt)).all()
        content_ids: list[ContentId] = []
        for attributes, unit_type in response:
            if unit_type == ProjectUnitType.DOCUMENT and attributes.get(
                "content_ref", None
            ):
                content_ids.append(ContentId(attributes["content_ref"]))

        return content_ids


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
