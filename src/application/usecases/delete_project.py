__all__ = ["DeleteProjectUsecase"]


from dataclasses import dataclass


from domain import Project, ProjectId
from application.ports.gateways import ProjectQueryGateway, ProjectCommandGateway
from application.exceptions import ProjectNotFoundError


@dataclass
class DeleteProjectRequest:
    project_id: ProjectId

    @classmethod
    def from_primitives(cls, project_id: str) -> "DeleteProjectRequest":
        return cls(project_id=ProjectId(project_id))


class DeleteProjectUsecase:

    def __init__(
        self,
        project_queries: ProjectQueryGateway,
        project_commands: ProjectCommandGateway,
    ):
        self._queries: ProjectQueryGateway = project_queries
        self._commands: ProjectCommandGateway = project_commands

    async def __call__(self, request: DeleteProjectRequest) -> None:
        try:
            found_project: Project = await self._queries.by_id(request.project_id.value)
        except ProjectNotFoundError:
            return

        await self._commands.delete(found_project)
