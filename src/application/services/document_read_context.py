from dataclasses import dataclass

from domain.entities import Document, DocumentId, Project, ProjectId, User
from domain.services import DocumentService
from application.ports import DocumentQueryGateway, ProjectQueryGateway
from application.exceptions import DocumentNotInProjectError
from application.exceptions.user import CurrentUserNotAssignError

from .current_user import CurrentUserService


@dataclass
class DocumentReadContext:

    current_user: User | None
    pinned_project: Project
    found_document: Document


class DocumentReadContextService:

    def __init__(
        self,
        current_user: CurrentUserService,
        document_queries: DocumentQueryGateway,
        project_queries: ProjectQueryGateway,
        document_service: DocumentService,
    ):
        self._current_user: CurrentUserService = current_user
        self._document_queries: DocumentQueryGateway = document_queries
        self._project_queries: ProjectQueryGateway = project_queries
        self._document_service: DocumentService = document_service

    async def __call__(
        self, project_id: ProjectId, document_id: DocumentId
    ) -> DocumentReadContext:
        project: Project = await self._project_queries.by_id(project_id.value)
        document: Document = await self._document_queries.by_id(document_id.value)

        if not self._document_service.belongs_to(document, project):
            raise DocumentNotInProjectError(
                "Members can only manage given project documents"
            )

        try:
            current_user: User | None = await self._current_user()
        except CurrentUserNotAssignError:
            current_user = None

        return DocumentReadContext(current_user, project, document)
