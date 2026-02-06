__all__ = [
    "GrantOwnerRequest",
    "GrantOwnerUsecase",
    "GrantOwnerResponse",
]


from datetime import datetime
from dataclasses import dataclass
from typing import TypedDict

from domain import User, UserId, Project, ProjectId
from domain.services import ProjectService
from domain.enums import ProjectRole
from application.ports import (
    ProjectQueryGateway,
    authorize,
    UserQueryGateway,
    ProjectCommandGateway,
    Clock,
)
from application.ports.authorization import (
    UserManagementContext,
    CanManageSelf,
)
from application.services import CurrentUserService


@dataclass
class GrantOwnerRequest:

    user_id: UserId
    project_id: ProjectId

    @classmethod
    def from_primitives(cls, user_id: str, project_id: str) -> "GrantOwnerRequest":
        return cls(
            user_id=UserId(user_id),
            project_id=ProjectId(project_id),
        )


class GrantOwnerResponse(TypedDict):

    old_owner_name: str
    old_owner_id: UserId
    old_owner_role: ProjectRole
    project: str

    @classmethod
    def from_entity(cls, old_owner: User, project: Project) -> "GrantOwnerResponse":
        return cls(
            old_owner_name=old_owner.name,
            old_owner_id=old_owner.id_,
            old_owner_role=project.members.get(UserId(old_owner.id_)),
            project=project.title,
        )


class GrantOwnerUsecase:

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

    async def __call__(self, request: GrantOwnerRequest) -> None:

        now: datetime = self._clock.now()
        current_user: User = await self._current_user()
        found_project: Project = await self._project_queries.by_id(
            request.project_id.value
        )

        owner: User = await self._user_queries.by_id(
            self._project_service.get_owner_id(found_project).value
        )

        authorize(
            CanManageSelf(),
            context=UserManagementContext(subject=current_user, target=owner),
        )

        updated_project: Project = self._project_service.grant_owner(
            found_project, request.user_id, now
        )
        await self._project_commands.update(updated_project)

        return GrantOwnerResponse.from_entity(owner, updated_project)
