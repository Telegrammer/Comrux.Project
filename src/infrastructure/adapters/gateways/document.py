from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities import Document, DocumentId
from application.exceptions import DocumentAlreadyExistsError
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
