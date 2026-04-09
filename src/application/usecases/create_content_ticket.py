from dataclasses import dataclass
from typing import TypedDict
from datetime import datetime
from domain.entities import (
    ProjectId,
    ProjectUnitId,
    DocumentId,
    ContentTicket,
    ContentTicketId,
    UserId,
)
from domain.entities.access_list import ResolvedUnitPermissions
from domain.entities.document import ContentId
from domain.services import ContentTicketService
from domain.value_objects import Name, PassedDatetime, FutureDatetime
from domain.enums import ProjectUnitAction
from application.ports import Clock
from application.services import (
    DocumentManageContext,
    DocumentManageContextService,
    ProjectUnitPermissionService,
)
from application.exceptions import AccessDeniedError


@dataclass
class CreateContentTicketRequest:
    project_id: ProjectId
    document_id: DocumentId

    @classmethod
    def from_primitives(
        cls, project_id: str, document_id: str
    ) -> "CreateContentTicketRequest":
        return cls(
            project_id=ProjectId(project_id),
            document_id=DocumentId(document_id),
        )


class CreateContentTicketResponse(TypedDict):
    ticket_id: ContentTicketId
    username: Name
    user_id: UserId
    project_id: ProjectId
    content_ref: ContentId
    permissions: list[ProjectUnitAction]
    issued_at: PassedDatetime
    expire_at: FutureDatetime

    @classmethod
    def from_entity(
        cls, entity: ContentTicket, project: ProjectId
    ) -> "CreateContentTicketResponse":
        return cls(
            ticket_id=entity.id_,
            username=entity.username,
            user_id=entity.user_id,
            project_id=project.value,
            content_ref=entity.content_ref,
            permissions=entity.permissions,
            issued_at=entity.issued_at,
            expire_at=entity.expire_at,
        )


class CreateContentTicketUsecase:
    def __init__(
        self,
        clock: Clock,
        context_service: DocumentManageContextService,
        permission_service: ProjectUnitPermissionService,
        content_ticket_service: ContentTicketService,
    ):
        self._clock = clock
        self._context_serivce = context_service
        self._permission_service = permission_service
        self._content_ticket_service = content_ticket_service

    async def __call__(self, request: CreateContentTicketRequest):

        now: datetime = self._clock.now()

        context: DocumentManageContext = await self._context_serivce(
            request.project_id, request.document_id
        )

        permissions: ResolvedUnitPermissions = await self._permission_service(
            context.current_user,
            context.pinned_project,
            ProjectUnitId(context.found_document.id_),
        )

        if ProjectUnitAction.READ in permissions.denied:
            raise AccessDeniedError(
                "Cannot enter to document edit because of acl's restrictions"
            )

        content_ticket: ContentTicket = self._content_ticket_service.create_ticket(
            user=context.current_user,
            now=now,
            permissions=list(permissions.allowed),
            content_ref=context.found_document.content_ref,
        )

        return CreateContentTicketResponse.from_entity(
            content_ticket, request.project_id
        )
