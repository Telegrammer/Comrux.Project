import logging

from dataclasses import dataclass
from domain.entities import DocumentId, ProjectId, User, Project, Document
from domain.services import DocumentService
from application.ports import DocumentQueryGateway, ProjectQueryGateway
from application.exceptions import DocumentNotInProjectError


from .current_user import CurrentUserService

logger = logging.getLogger(__name__)


@dataclass
class DocumentManageContext:

    current_user: User
    pinned_project: Project
    found_document: Document


class DocumentManageContextService:

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
    ) -> DocumentManageContext:

        current_user: User = await self._current_user()
        project: Project = await self._project_queries.by_id(project_id.value)
        document: Document = await self._document_queries.by_id(document_id.value)

        if not self._document_service.belongs_to(document, project):
            raise DocumentNotInProjectError(
                "Members can only manage given project documents"
            )

        return DocumentManageContext(current_user, project, document)
