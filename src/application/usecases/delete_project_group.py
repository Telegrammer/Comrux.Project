from dataclasses import dataclass

from domain.entities import ProjectGroupId, ProjectId, UserId
from domain.enums import ProjectRole

from application.exceptions import AccessDeniedError
from application.ports.gateways import ProjectGroupCommandGateway
from application.services import ProjectGroupManageContextService


@dataclass
class DeleteProjectGroupRequest:
    project_id: ProjectId
    group_id: ProjectGroupId

    @classmethod
    def from_primitives(
        cls, project_id: str, group_id: str
    ) -> "DeleteProjectGroupRequest":
        return cls(project_id=ProjectId(project_id), group_id=ProjectGroupId(group_id))


class DeleteProjectGroupUsecase:
    def __init__(
        self,
        context_service: ProjectGroupManageContextService,
        group_commands: ProjectGroupCommandGateway,
    ) -> None:
        self._context_service = context_service
        self._group_commands = group_commands

    async def __call__(self, request: DeleteProjectGroupRequest) -> None:
        context = await self._context_service(request.project_id, request.group_id)
        current_user_id = UserId(context.current_user.id_)
        project_role = context.pinned_project.members.get(current_user_id)

        if not (
            context.found_group.owner != current_user_id
            or project_role != ProjectRole.OWNER
        ):
            raise AccessDeniedError(
                "Only group owner or project owner can delete group"
            )

        await self._group_commands.delete(context.found_group)
