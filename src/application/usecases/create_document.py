import asyncio
from datetime import datetime
from typing import TypedDict
from dataclasses import dataclass

from domain.value_objects import FileName
from domain.entities import (
    ProjectId,
    DirectoryId,
    Document,
    DocumentId,
    UserId,
)
from domain.entities.document import ContentId
from domain.services import DocumentService
from application.ports import (
    DocumentCommandGateway,
    Clock,
)
from application.ports.authorization import (
    authorize,
    CanManageProjectContent,
    ProjectContentManagmentContext,
)
from application.services import (
    DirectoryManageContext,
    DirectoryManageContextService,
)


@dataclass
class CreateDocumentRequest:

    project_id: ProjectId
    parent_id: DirectoryId
    name: FileName

    @classmethod
    def from_primitives(
        cls, project: str, parent: str, name: str
    ) -> "CreateDocumentRequest":
        return cls(
            project_id=ProjectId(project),
            parent_id=DirectoryId(parent),
            name=FileName(name),
        )


class CreateDocumentResponse(TypedDict):

    document: DocumentId
    content_ref: ContentId


class CreateDocumentUsecase:

    def __init__(
        self,
        clock: Clock,
        context_service: DirectoryManageContextService,
        document_service: DocumentService,
        document_commands: DocumentCommandGateway,
    ):
        self._clock = clock
        self._context_service: DirectoryManageContextService = context_service
        self._document_service: DocumentService = document_service
        self._document_commands: DocumentCommandGateway = document_commands

    async def __call__(self, request: CreateDocumentRequest) -> CreateDocumentResponse:
        now: datetime = self._clock.now()

        context: DirectoryManageContext = await self._context_service(
            request.project_id, request.parent_id
        )

        authorize(
            CanManageProjectContent(),
            context=ProjectContentManagmentContext(
                subject=context.current_user, target=context.pinned_project
            ),
        )

        new_document: Document = self._document_service.create_document(
            project=context.pinned_project,
            name=request.name,
            parent=context.parent_directory,
            creator=UserId(context.current_user.id_),
            now=now,
        )
        await self._document_commands.add(new_document)
        return CreateDocumentResponse(
            document=new_document.id_, content_ref=new_document.content_ref
        )
