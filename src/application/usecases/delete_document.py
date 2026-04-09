from dataclasses import dataclass

from domain import DocumentId, ProjectId, ProjectUnitId
from domain.entities.access_list import ResolvedUnitPermissions
from domain.entities.document import ContentId
from domain.enums import ProjectUnitAction

from application.exceptions import AccessDeniedError, DocumentNotFoundError
from application.ports import DocumentCommandGateway
from application.services import (
    DocumentManageContext,
    DocumentManageContextService,
    ProjectUnitPermissionService,
)


@dataclass
class DeleteDocumentRequest:
    project_id: ProjectId
    document_id: DocumentId

    @classmethod
    def from_primitives(
        cls, project_id: str, document_id: str
    ) -> "DeleteDocumentRequest":
        return cls(
            project_id=ProjectId(project_id), document_id=DocumentId(document_id)
        )


@dataclass(frozen=True, slots=True)
class DeleteDocumentResponse:
    project_id: ProjectId
    content_ids: tuple[ContentId, ...]
    deleted: bool
    message: str


class DeleteDocumentUsecase:
    def __init__(
        self,
        context_service: DocumentManageContextService,
        permission_service: ProjectUnitPermissionService,
        document_commands: DocumentCommandGateway,
    ):
        self._context_service: DocumentManageContextService = context_service
        self._permission_service = permission_service
        self._document_commands: DocumentCommandGateway = document_commands

    async def __call__(
        self, request: DeleteDocumentRequest
    ) -> DeleteDocumentResponse:

        try:
            context: DocumentManageContext = await self._context_service(
                request.project_id, request.document_id
            )
        except DocumentNotFoundError:
            return DeleteDocumentResponse(
                project_id=request.project_id,
                content_ids=(),
                deleted=False,
                message="Document is already deleted or never been in system",
            )

        permissions: ResolvedUnitPermissions = await self._permission_service(
            context.current_user,
            context.pinned_project,
            ProjectUnitId(context.found_document.parent.value),
        )

        if ProjectUnitAction.WRITE in permissions.denied:
            raise AccessDeniedError(
                "Cannot delete document. Parent directory have restrictions by acls"
            )

        await self._document_commands.delete(context.found_document.id_)
        return DeleteDocumentResponse(
            project_id=request.project_id,
            content_ids=(context.found_document.content_ref,),
            deleted=True,
            message="Document deleted",
        )
