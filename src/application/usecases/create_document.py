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
    ProjectUnitId,
)
from domain.enums import ProjectUnitAction
from domain.entities.access_list import ResolvedUnitPermissions
from domain.entities.document import ContentId
from domain.services import DocumentService
from application.ports import (
    DocumentCommandGateway,
    Clock,
)
from application.services import (
    DirectoryManageContext,
    DirectoryManageContextService,
    ProjectUnitPermissionService,
)
from application.exceptions import AccessDeniedError


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
        permission_service: ProjectUnitPermissionService,
        document_service: DocumentService,
        document_commands: DocumentCommandGateway,
    ):
        self._clock = clock
        self._context_service: DirectoryManageContextService = context_service
        self._permission_service = permission_service
        self._document_service: DocumentService = document_service
        self._document_commands: DocumentCommandGateway = document_commands

    async def __call__(self, request: CreateDocumentRequest) -> CreateDocumentResponse:
        now: datetime = self._clock.now()

        context: DirectoryManageContext = await self._context_service(
            request.project_id, request.parent_id
        )

        permissions: ResolvedUnitPermissions = await self._permission_service(
            context.current_user,
            context.pinned_project,
            ProjectUnitId(context.found_directory.id_),
        )

        if ProjectUnitAction.WRITE in permissions.denied:
            raise AccessDeniedError(
                "Cannot create document. Parent directory have restrictions by acls"
            )

        new_document: Document = self._document_service.create_document(
            project=context.pinned_project,
            name=request.name,
            parent=context.found_directory,
            creator=UserId(context.current_user.id_),
            now=now,
        )
        await self._document_commands.add(new_document)
        return CreateDocumentResponse(
            document=new_document.id_, content_ref=new_document.content_ref
        )
