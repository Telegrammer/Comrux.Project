__all__ = ["UpdateProjectUsecase"]

from datetime import datetime
from dataclasses import dataclass
from domain.value_objects import Title
from domain import Project, ProjectId
from domain.services import ProjectService

from application.ports import Clock
from application.ports.gateways import (
    ProjectQueryGateway,
    ProjectCommandGateway,
)
from application.exceptions import ProjectNotFoundError


@dataclass
class UpdateProjectRequest:

    project_id: ProjectId
    title: Title
    description: str

    @classmethod
    def from_primitives(
        cls, project_id: str, title: str, description: str
    ) -> "UpdateProjectRequest":
        return cls(
            project_id=ProjectId(project_id),
            title=Title(title),
            description=description,
        )


class UpdateProjectUsecase:

    def __init__(
        self,
        clock: Clock,
        project_service: ProjectService,
        project_queries: ProjectQueryGateway,
        project_commands: ProjectCommandGateway,
    ):
        self._clock: Clock = clock
        self._project_service: ProjectService = project_service
        self._queries: ProjectQueryGateway = project_queries
        self._commands: ProjectCommandGateway = project_commands

    async def __call__(self, request: UpdateProjectRequest) -> None:
        now: datetime = self._clock.now()
        found_project: Project = await self._queries.by_id(request.project_id.value)

        await self._commands.update(
            self._project_service.update_project(
                project=found_project,
                title=request.title,
                description=request.description,
                now=now,
            )
        )
