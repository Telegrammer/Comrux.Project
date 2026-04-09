from dataclasses import dataclass

from domain.entities import DocumentId, ProjectId, ProjectUnitId
from domain.enums import ProjectUnitAction
from domain.entities.access_list import ResolvedUnitPermissions
from application.ports import ContentQueryGateway
from application.services import DocumentReadContext, DocumentReadContextService
from application.services.project_unit_permission import ProjectUnitPermissionService
from application.exceptions import AccessDeniedError


@dataclass
class GetDocumentContentRequest:

    project_id: ProjectId
    document_id: DocumentId

    @classmethod
    def from_primitives(
        cls, project_id: str, document_id: str
    ) -> "GetDocumentContentRequest":
        return cls(
            project_id=ProjectId(project_id),
            document_id=DocumentId(document_id),
        )


class GetDocumentContentUsecase:

    def __init__(
        self,
        context_service: DocumentReadContextService,
        permission_service: ProjectUnitPermissionService,
        content_queries: ContentQueryGateway,
    ):
        self._context_service: DocumentReadContextService = context_service
        self._permission_service: ProjectUnitPermissionService = permission_service
        self._content_queries: ContentQueryGateway = content_queries

    async def __call__(self, request: GetDocumentContentRequest) -> bytes:
        context: DocumentReadContext = await self._context_service(
            request.project_id, request.document_id
        )

        if context.pinned_project.is_private:
            if context.current_user is None:
                raise AccessDeniedError(
                    "Cannot read document content because project is private"
                )

            permissions: ResolvedUnitPermissions = await self._permission_service(
                context.current_user,
                context.pinned_project,
                ProjectUnitId(context.found_document.id_),
            )

            if ProjectUnitAction.READ in permissions.denied:
                raise AccessDeniedError(
                    "Cannot read document content because of acl's restrictions"
                )

        return await self._content_queries.by_location(
            request.project_id, context.found_document.content_ref
        )
