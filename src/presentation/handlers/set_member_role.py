from application.compositions import SetMemberRoleComposition
from presentation.models import ProjectSetMemberRole, ProjectMemberRoleReassigned
from application.usecases import SetMemberRoleRequest, SetMemberRoleResponse


class SetMemberRoleHandler:

    def __init__(self, usecase: SetMemberRoleComposition):
        self._usecase = usecase

    async def __call__(
        self, project_id: str, member_id: str, request: ProjectSetMemberRole
    ) -> ProjectMemberRoleReassigned:

        response: SetMemberRoleResponse = await self._usecase(
            SetMemberRoleRequest.from_primitives(
                str(member_id), str(project_id), request.role
            )
        )

        return ProjectMemberRoleReassigned(
            member=response["member_name"],
            old_role=response["old_role"],
            project=response["project"],
        )
