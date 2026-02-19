from dataclasses import dataclass
from domain import DocumentId, ProjectId, User, Project, Document


from application.ports import (
    DocumentCommandGateway,
    ProjectQueryGateway,
    DocumentQueryGateway,
)
from application.services import DocumentManageContext, DocumentManageContextService
from application.exceptions import DocumentNotFoundError, DocumentNotInProjectError
from application.ports.authorization import (
    authorize,
    CanManageProjectContent,
    ProjectContentManagmentContext,
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


# TODO: add task gateway for content deletion
# TODO: rethink about ProjectUnitContextSerivce
class DeleteDocumentUsecase:

    def __init__(
        self,
        context_service: DocumentManageContextService,
        document_commands: DocumentCommandGateway,
    ):
        self._context_service: DocumentManageContextService = context_service
        self._document_commands: DocumentCommandGateway = document_commands

    async def __call__(self, request: DeleteDocumentRequest) -> str:

        try:
            context: DocumentManageContext = await self._context_service(
                request.project_id.value, request.document_id.value
            )
        except DocumentNotFoundError:
            return "Document is already deleted or never been in system"

        authorize(
            CanManageProjectContent(),
            context=ProjectContentManagmentContext(
                subject=context.current_user, target=context.pinned_project
            ),
        )
        
        await self._document_commands.delete(context.found_document.id_)
        return "Document deleted"
