import logging

from dataclasses import dataclass
from domain.entities import DirectoryId, ProjectId, User, Project, Directory
from application.ports import DirectoryQueryGateway, ProjectQueryGateway


from .current_user import CurrentUserService

logger = logging.getLogger(__name__)


@dataclass
class ProjectUnitCreationContext:

    current_user: User
    pinned_project: Project
    parent_directory: Directory


class ProjectUnitCreationContextService:

    def __init__(
        self,
        current_user: CurrentUserService,
        directory_queries: DirectoryQueryGateway,
        project_queries: ProjectQueryGateway,
    ):
        self._current_user: CurrentUserService = current_user
        self._directory_queries: DirectoryQueryGateway = directory_queries
        self._project_queries: ProjectQueryGateway = project_queries

    async def __call__(
        self, project_id: ProjectId, directory_id: DirectoryId
    ) -> ProjectUnitCreationContext:

        current_user: User = await self._current_user()
        project: Project = await self._project_queries.by_id(project_id.value)
        directory: Directory = await self._directory_queries.by_id(directory_id.value)

        return ProjectUnitCreationContext(
            current_user,
            project,
            directory,
        )
