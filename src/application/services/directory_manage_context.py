from dataclasses import dataclass

from domain import DirectoryId, Project, ProjectId, User
from domain.entities import Directory

from application.exceptions import DirectoryNotInProjectError
from application.ports.gateways import DirectoryQueryGateway, ProjectQueryGateway
from application.services import CurrentUserService


@dataclass
class DirectoryManageContext:
    current_user: User
    pinned_project: Project
    found_directory: Directory


class DirectoryManageContextService:
    def __init__(
        self,
        current_user: CurrentUserService,
        directory_queries: DirectoryQueryGateway,
        project_queries: ProjectQueryGateway,
    ) -> None:
        self._current_user = current_user
        self._directory_queries = directory_queries
        self._project_queries = project_queries

    async def __call__(
        self, project_id: ProjectId, directory_id: DirectoryId
    ) -> DirectoryManageContext:
        current_user: User = await self._current_user()
        project: Project = await self._project_queries.by_id(project_id.value)
        directory: Directory = await self._directory_queries.by_id(directory_id.value)

        if directory.project.value != project.id_:
            raise DirectoryNotInProjectError("Given directory is not in given project")

        return DirectoryManageContext(
            current_user=current_user,
            pinned_project=project,
            found_directory=directory,
        )
