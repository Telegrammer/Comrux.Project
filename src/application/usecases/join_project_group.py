from dataclasses import dataclass

from domain.entities import ProjectGroupId, ProjectId, UserId
from domain.services import ProjectGroupService

from application.exceptions import (
    ProjectGroupParticipantNotInProjectError,
)
from application.ports.gateways import ProjectGroupCommandGateway, UserQueryGateway
from application.ports.authorization import (
    authorize,
    CanAddGroupParticipant,
    ProjectGroupParticipantManagmentContext,
)
from application.services import ProjectGroupManageContextService


@dataclass
class JoinProjectGroupRequest:
    project_id: ProjectId
    group_id: ProjectGroupId
    participant_id: UserId

    @classmethod
    def from_primitives(
        cls,
        project_id: str,
        group_id: str,
        participant_id: str,
    ) -> "JoinProjectGroupRequest":
        return cls(
            project_id=ProjectId(project_id),
            group_id=ProjectGroupId(group_id),
            participant_id=UserId(participant_id),
        )


class JoinProjectGroupUsecase:
    def __init__(
        self,
        context_service: ProjectGroupManageContextService,
        user_queries: UserQueryGateway,
        group_service: ProjectGroupService,
        group_commands: ProjectGroupCommandGateway,
    ) -> None:
        self._context_service = context_service
        self._user_queries = user_queries
        self._group_service = group_service
        self._group_commands = group_commands

    async def __call__(self, request: JoinProjectGroupRequest) -> None:
        context = await self._context_service(request.project_id, request.group_id)
        current_user_id = UserId(context.current_user.id_)

        participant = await self._user_queries.by_id(request.participant_id.value)

        participant_role = context.pinned_project.members.get(request.participant_id)
        if participant_role is None:
            raise ProjectGroupParticipantNotInProjectError(
                "Only project members can be added to project group"
            )

        is_self_join = current_user_id == request.participant_id
        if not (context.found_group.is_public and is_self_join):
            authorize(
                CanAddGroupParticipant(),
                context=ProjectGroupParticipantManagmentContext(
                    subject=context.current_user,
                    project=context.pinned_project,
                    target=participant,
                ),
            )

        updated_group = self._group_service.join(
            context.found_group,
            participant_id=request.participant_id,
            actor_id=current_user_id,
        )
        await self._group_commands.update(updated_group)
