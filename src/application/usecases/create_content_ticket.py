from dataclasses import dataclass
from typing import TypedDict
from datetime import datetime
from domain.entities import (
    ProjectId,
    DocumentId,
    ContentTicket,
    ContentTicketId,
    UserId,
)
from domain.entities.document import ContentId
from domain.services import ContentTicketService
from domain.value_objects import Name, PassedDatetime, FutureDatetime
from domain.enums import ContentPermission
from application.ports import ProjectQueryGateway, DocumentQueryGateway, Clock
from application.services import DocumentManageContext, DocumentManageContextService
from application.ports.authorization import (
    CanManageProjectContent,
    authorize,
    ProjectContentManagmentContext,
)


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
    content_ref: ContentId
    permissions: list[ContentPermission]
    issued_at: PassedDatetime
    expire_at: FutureDatetime

    @classmethod
    def from_entity(cls, entity: ContentTicket) -> "CreateContentTicketResponse":
        return cls(
            ticket_id=entity.id_,
            username=entity.username,
            user_id=entity.user_id,
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
        content_ticket_service: ContentTicketService,
    ):
        self._clock = clock
        self._context_serivce = context_service
        self._content_ticket_service = content_ticket_service

    async def __call__(self, request: CreateContentTicketRequest):

        now: datetime = self._clock.now()

        context: DocumentManageContext = await self._context_serivce(
            request.project_id, request.document_id
        )
        authorize(
            CanManageProjectContent(),
            context=ProjectContentManagmentContext(
                subject=context.current_user, target=context.pinned_project
            ),
        )

        # TODO: MOVE CONSTANS IN OTHER SERVICE AFTER ACL DEFENITION
        permissions: list[ContentPermission] = [
            ContentPermission.VIEW,
            ContentPermission.EDIT,
        ]

        content_ticket: ContentTicket = self._content_ticket_service.create_ticket(
            user=context.current_user,
            now=now,
            permissions=permissions,
            content_ref=context.found_document.content_ref,
        )

        return CreateContentTicketResponse.from_entity(content_ticket)
