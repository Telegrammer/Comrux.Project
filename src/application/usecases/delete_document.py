from dataclasses import dataclass
from domain import DocumentId, ProjectId, User, Project, Document


from application.ports import (
    DocumentCommandGateway,
    ProjectQueryGateway,
    DocumentQueryGateway,
)
from application.services import CurrentUserService
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
        current_user: CurrentUserService,
        project_gateway: ProjectQueryGateway,
        document_queries: DocumentQueryGateway,
        document_commands: DocumentCommandGateway,
    ):
        self._current_user: CurrentUserService = current_user
        self._project_gateway: ProjectQueryGateway = project_gateway
        self._document_queries: DocumentQueryGateway = document_queries
        self._document_commands: DocumentCommandGateway = document_commands

    async def __call__(self, request: DeleteDocumentRequest) -> str:

        current_user: User = await self._current_user()
        found_project: Project = await self._project_gateway.by_id(
            request.project_id.value
        )

        authorize(
            CanManageProjectContent(),
            context=ProjectContentManagmentContext(
                subject=current_user, target=found_project
            ),
        )

        try:
            found_document: Document = await self._document_queries.by_id(
                request.document_id.value
            )
        except DocumentNotFoundError:
            return "Document is already deleted or never been in system"

        if found_document.project.value != found_project.id_:
            raise DocumentNotInProjectError("Given document is not in given project")

        await self._document_commands.delete(found_document.id_)
        return "Document deleted"
