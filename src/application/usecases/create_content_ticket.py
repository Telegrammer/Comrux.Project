from dataclasses import dataclass
from typing import TypedDict
from datetime import datetime
from domain.entities import (
    ProjectId,
    ProjectGroup,
    ProjectGroupId,
    ProjectUnitId,
    DocumentId,
    ContentTicket,
    ContentTicketId,
    UserId,
)
from domain.entities.access_list import ResolvedUnitPermissions
from domain.entities.document import ContentId
from domain.services import ContentTicketService
from domain.value_objects import Name, PassedDatetime, FutureDatetime, Title, Color
from domain.enums import ProjectUnitAction
from application.ports import Clock
from application.ports.gateways import ProjectGroupQueryGateway
from application.services import (
    DocumentManageContext,
    DocumentManageContextService,
    ProjectUnitPermissionService,
)
from application.exceptions import (
    AccessDeniedError,
    ProjectGroupNotInProjectError,
    UserNotInProjectGroupError,
)


@dataclass
class CreateContentTicketRequest:
    project_id: ProjectId
    document_id: DocumentId
    team_id: ProjectGroupId | None = None

    @classmethod
    def from_primitives(
        cls,
        project_id: str,
        document_id: str,
        team_id: str | None = None,
    ) -> "CreateContentTicketRequest":
        return cls(
            project_id=ProjectId(project_id),
            document_id=DocumentId(document_id),
            team_id=ProjectGroupId(team_id) if team_id is not None else None,
        )


class BaseCreateContentTicketResponse(TypedDict):
    ticket_id: ContentTicketId
    username: Name
    user_id: UserId
    project_id: ProjectId
    content_ref: ContentId
    permissions: list[ProjectUnitAction]
    issued_at: PassedDatetime
    expire_at: FutureDatetime


class CreateContentTicketResponse(BaseCreateContentTicketResponse, total=False):
    team_id: ProjectGroupId
    team_name: Title
    team_color: Color

    @classmethod
    def from_entity(
        cls,
        entity: ContentTicket,
        project: ProjectId,
        group: ProjectGroup | None = None,
    ) -> "CreateContentTicketResponse":
        response: CreateContentTicketResponse = cls(
            ticket_id=entity.id_,
            username=entity.username,
            user_id=entity.user_id,
            project_id=project.value,
            content_ref=entity.content_ref,
            permissions=entity.permissions,
            issued_at=entity.issued_at,
            expire_at=entity.expire_at,
        )
        if group is not None:
            response["team_id"] = group.id_
            response["team_name"] = group.name
            response["team_color"] = group.color
        return response


class CreateContentTicketUsecase:
    def __init__(
        self,
        clock: Clock,
        context_service: DocumentManageContextService,
        permission_service: ProjectUnitPermissionService,
        content_ticket_service: ContentTicketService,
        group_queries: ProjectGroupQueryGateway,
    ):
        self._clock = clock
        self._context_serivce = context_service
        self._permission_service = permission_service
        self._content_ticket_service = content_ticket_service
        self._group_queries = group_queries

    async def __call__(
        self, request: CreateContentTicketRequest
    ) -> CreateContentTicketResponse:

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

        group: ProjectGroup | None = None
        if request.team_id is not None:
            group = await self._group_queries.by_id(request.team_id.value)
            if group.project_id != request.project_id.value:
                raise ProjectGroupNotInProjectError(
                    "Selected group does not belong to project"
                )
            current_user_id = context.current_user.id_
            if UserId(current_user_id) not in group.participants:
                raise UserNotInProjectGroupError(
                    "Current user is not in selected group"
                )

        content_ticket: ContentTicket = self._content_ticket_service.create_ticket(
            user=context.current_user,
            now=now,
            permissions=list(permissions.allowed),
            content_ref=context.found_document.content_ref,
        )
        return CreateContentTicketResponse.from_entity(
            content_ticket, request.project_id, group
        )
