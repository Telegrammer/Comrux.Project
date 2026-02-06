__all__ = [
    "RemoveProjectMemberRequest",
    "RemoveProjectMemberUsecase",
    "RemoveProjectMemberResponse",
]


from dataclasses import dataclass
from typing import TypedDict
from datetime import datetime

from domain import User, UserId, Project, ProjectId
from domain.services import ProjectService
from application.services import CurrentUserService
from application.ports import (
    ProjectCommandGateway,
    ProjectQueryGateway,
    UserQueryGateway,
    Clock,
)
from application.ports.authorization import (
    CanUpdateProject,
    ProjectManagmentContext,
    authorize,
)
from application.exceptions import UserNotFoundError, ProjectNotFoundError


@dataclass
class RemoveProjectMemberRequest:

    user_id: UserId
    project_id: ProjectId

    @classmethod
    def from_primitives(cls, user: str, project: str) -> "RemoveProjectMemberRequest":
        return cls(user_id=UserId(user), project_id=ProjectId(project))


class RemoveProjectMemberResponse(TypedDict):

    member: UserId
    project: str

    @classmethod
    def from_entity(
        cls, member: UserId, project: Project
    ) -> "RemoveProjectMemberResponse":
        return cls(
            member=member,
            project=project.title,
        )


class RemoveProjectMemberUsecase:

    def __init__(
        self,
        clock: Clock,
        current_user: CurrentUserService,
        user_queries: UserQueryGateway,
        project_service: ProjectService,
        project_queries: ProjectQueryGateway,
        project_commands: ProjectCommandGateway,
    ):
        self._clock = clock
        self._current_user: CurrentUserService = current_user
        self._user_queries: UserQueryGateway = user_queries
        self._project_service: ProjectService = project_service
        self._project_queries: ProjectQueryGateway = project_queries
        self._project_commands: ProjectCommandGateway = project_commands

    async def __call__(
        self, request: RemoveProjectMemberRequest
    ) -> RemoveProjectMemberResponse:

        now: datetime = self._clock.now()

        found_project: Project = await self._project_queries.by_id(
            request.project_id.value
        )

        current_user: User = await self._current_user()
        authorize(
            CanUpdateProject(),
            context=ProjectManagmentContext(subject=current_user, target=found_project),
        )

        updated_project: Project = self._project_service.remove_member(
            found_project, request.user_id, now
        )
        await self._project_commands.update(updated_project)

        return RemoveProjectMemberResponse.from_entity(
            request.user_id.value, updated_project
        )
