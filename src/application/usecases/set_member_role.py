__all__ = [
    "SetMemberRoleRequest",
    "SetMemberRoleUsecase",
    "SetMemberRoleResponse",
]


from datetime import datetime
from dataclasses import dataclass
from typing import TypedDict

from domain import User, UserId, Project, ProjectId
from domain.services import ProjectService
from domain.enums import ProjectRole
from domain.exceptions import MemberNotFoundError
from application.ports import (
    ProjectQueryGateway,
    authorize,
    UserQueryGateway,
    ProjectCommandGateway,
    Clock,
)
from application.ports.authorization import (
    RoleManagementContext,
    CanManageRole,
)
from application.services import CurrentUserService


@dataclass
class SetMemberRoleRequest:

    user_id: UserId
    project_id: ProjectId
    new_role: ProjectRole

    @classmethod
    def from_primitives(
        cls, user_id: str, project_id: str, role: str
    ) -> "SetMemberRoleRequest":
        return cls(
            user_id=UserId(user_id),
            project_id=ProjectId(project_id),
            new_role=ProjectRole(role),
        )


class SetMemberRoleResponse(TypedDict):

    member_name: str
    old_role: ProjectRole
    project: str

    @classmethod
    def from_entity(cls, member: User, old_project: Project) -> "SetMemberRoleResponse":
        return cls(
            member_name=member.name,
            old_role=old_project.members.get(UserId(member.id_)),
            project=old_project.title,
        )


class SetMemberRoleUsecase:

    def __init__(
        self,
        clock: Clock,
        project_service: ProjectService,
        project_queries: ProjectQueryGateway,
        project_commands: ProjectCommandGateway,
        current_user: CurrentUserService,
        user_queries: UserQueryGateway,
    ):
        self._clock: Clock = clock
        self._project_service: ProjectService = project_service
        self._project_queries: ProjectQueryGateway = project_queries
        self._project_commands: ProjectCommandGateway = project_commands
        self._current_user: CurrentUserService = current_user
        self._user_queries: UserQueryGateway = user_queries

    async def __call__(self, request: SetMemberRoleRequest) -> SetMemberRoleResponse:

        now: datetime = self._clock.now()
        current_user: User = await self._current_user()
        found_project: Project = await self._project_queries.by_id(
            request.project_id.value
        )

        member: User = await self._user_queries.by_id(request.user_id.value)
        member_role: ProjectRole = found_project.members.get(UserId(member.id_))

        if not member_role:
            raise MemberNotFoundError("Project does not have member with given id")

        authorize(
            CanManageRole(),
            context=RoleManagementContext(
                subject_role=found_project.members.get(UserId(current_user.id_)),
                target_role=member_role,
                new_role=request.new_role,
            ),
        )

        updated_project: Project = self._project_service.set_role(
            found_project, UserId(member.id_), request.new_role, now
        )
        await self._project_commands.update(updated_project)

        return SetMemberRoleResponse.from_entity(member, found_project)
