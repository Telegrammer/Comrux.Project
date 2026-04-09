from dataclasses import dataclass
from domain import Project, ProjectId, User
from domain.services import ProjectService

from application.services import CurrentUserService
from application.ports import Clock
from application.ports.gateways import (
    ProjectQueryGateway,
    ProjectCommandGateway,
)
from application.ports.authorization import (
    CanChangePrivateness,
    ProjectManagmentContext,
    authorize,
)


@dataclass
class SetProjectAccessRequest:
    project_id: ProjectId
    is_private: bool

    @classmethod
    def from_primitives(
        cls, project_id: str, is_private: bool
    ) -> "SetProjectAccessRequest":
        return cls(project_id=ProjectId(project_id), is_private=is_private)


class SetProjectAccessUsecase:
    def __init__(
        self,
        clock: Clock,
        project_service: ProjectService,
        project_queries: ProjectQueryGateway,
        project_commands: ProjectCommandGateway,
        current_user: CurrentUserService,
    ):
        self._clock: Clock = clock
        self._project_service: ProjectService = project_service
        self._queries: ProjectQueryGateway = project_queries
        self._commands: ProjectCommandGateway = project_commands
        self._current_user: CurrentUserService = current_user

    async def __call__(self, request: SetProjectAccessRequest) -> None:
        found_project: Project = await self._queries.by_id(request.project_id.value)

        current_user: User = await self._current_user()

        authorize(
            CanChangePrivateness(),
            context=ProjectManagmentContext(subject=current_user, target=found_project),
        )

        found_project.is_private = request.is_private

        await self._commands.update(found_project)
