from dataclasses import dataclass

from domain.entities import ProjectGroupId, ProjectId, UserId
from domain.services import ProjectGroupService

from application.exceptions import AccessDeniedError
from application.ports.gateways import ProjectGroupCommandGateway
from application.services import ProjectGroupManageContextService


@dataclass
class LeaveProjectGroupRequest:
    project_id: ProjectId
    group_id: ProjectGroupId
    participant_id: UserId

    @classmethod
    def from_primitives(
        cls,
        project_id: str,
        group_id: str,
        participant_id: str,
    ) -> "LeaveProjectGroupRequest":
        return cls(
            project_id=ProjectId(project_id),
            group_id=ProjectGroupId(group_id),
            participant_id=UserId(participant_id),
        )


class LeaveProjectGroupUsecase:
    def __init__(
        self,
        context_service: ProjectGroupManageContextService,
        group_service: ProjectGroupService,
        group_commands: ProjectGroupCommandGateway,
    ) -> None:
        self._context_service = context_service
        self._group_service = group_service
        self._group_commands = group_commands

    async def __call__(self, request: LeaveProjectGroupRequest) -> None:
        context = await self._context_service(request.project_id, request.group_id)
        current_user_id = UserId(context.current_user.id_)

        if (
            current_user_id != request.participant_id
            and current_user_id != context.found_group.owner
        ):
            raise AccessDeniedError(
                "Only participant himself or group owner can remove member"
            )

        updated_group = self._group_service.leave(
            context.found_group,
            participant_id=request.participant_id,
        )
        await self._group_commands.update(updated_group)
