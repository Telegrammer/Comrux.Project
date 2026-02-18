from functools import singledispatchmethod
from sqlalchemy import select, delete as sql_delete, Delete
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities import Document, DocumentId
from application.exceptions import DocumentAlreadyExistsError, DocumentNotFoundError
from infrastructure.adapters.mappers import SqlAlchemyDocumentMapper
from infrastructure.exceptions.error_aware_decorators import network_error_aware
from infrastructure.exceptions.asyncpg_unique_error_handler import (
    unique_violation_aware,
)
from infrastructure.models import ProjectUnitNode


class SqlAlchemyDocumentCommandGateway:

    def __init__(self, mapper: SqlAlchemyDocumentMapper, session: AsyncSession):
        self._mapper: SqlAlchemyDocumentMapper = mapper
        self._session: AsyncSession = session

    @network_error_aware("Cannot create document: docs are unavailable via network")
    @unique_violation_aware(
        DocumentAlreadyExistsError(
            "Document with the same name and parent directory already exsists"
        )
    )
    async def add(self, document: Document) -> None:

        node: ProjectUnitNode = self._mapper.to_dto(document)
        self._session.add(node)
        await self._session.flush()

    @network_error_aware("Cannot delete document: document are unreachable via network")
    async def delete(self, document_id: DocumentId) -> None:
        stmt: Delete = sql_delete(ProjectUnitNode).where(
            ProjectUnitNode.id_ == document_id
        )
        await self._session.execute(stmt)



class SqlAlchemyDocumentQueryGateway:

    def __init__(self, mapper: SqlAlchemyDocumentMapper, session: AsyncSession):
        self._mapper: SqlAlchemyDocumentMapper = mapper
        self._session: AsyncSession = session

    @network_error_aware("Cannot find directory: directories are unavailable")
    async def by_id(self, directory_id: DocumentId) -> Document:

        stmt = select(ProjectUnitNode).where(ProjectUnitNode.id_ == directory_id)
        node: ProjectUnitNode | None = (
            await self._session.execute(stmt)
        ).scalar_one_or_none()

        if not node:
            raise DocumentNotFoundError("Directory with given id does not exists")

        return self._mapper.to_domain(node)