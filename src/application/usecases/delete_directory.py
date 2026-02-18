from dataclasses import dataclass
from domain import Directory, ProjectId, User, Project, DirectoryId


from domain import DirectoryService
from application.ports import (
    ProjectQueryGateway,
    DirectoryCommandGateway,
    DirectoryQueryGateway,
)
from application.services import CurrentUserService
from application.exceptions import (
    DirectoryNotInProjectError,
    DirectoryNotFoundError,
    AccessDeniedError,
)
from application.ports.authorization import (
    authorize,
    CanManageProjectContent,
    ProjectContentManagmentContext,
)


@dataclass
class DeleteDirectoryRequest:

    project_id: ProjectId
    directory_id: DirectoryId

    @classmethod
    def from_primitives(
        cls, project_id: str, directory_id: str
    ) -> "DeleteDirectoryRequest":
        return cls(
            project_id=ProjectId(project_id), directory_id=DirectoryId(directory_id)
        )


# TODO: add task gateway for content deletion
# TODO: rethink about ProjectUnitContextSerivce
class DeleteDirectoryUsecase:

    def __init__(
        self,
        current_user: CurrentUserService,
        project_gateway: ProjectQueryGateway,
        directory_queries: DirectoryQueryGateway,
        directory_commands: DirectoryCommandGateway,
        directory_service: DirectoryService,
    ):
        self._current_user: CurrentUserService = current_user
        self._project_gateway: ProjectQueryGateway = project_gateway
        self._directory_queries: DirectoryQueryGateway = directory_queries
        self._directory_commands: DirectoryCommandGateway = directory_commands
        self._directory_service: DirectoryService = directory_service

    async def __call__(self, request: DeleteDirectoryRequest) -> str:

        current_user: User = await self._current_user()
        found_project: Project = await self._project_gateway.by_id(
            request.project_id.value
        )

        authorize(
            CanManageProjectContent(),
            context=ProjectContentManagmentContext(
                subject=current_user, target=found_project
            ),
        )

        try:
            found_directory: Directory = await self._directory_queries.by_id(
                request.directory_id.value
            )
        except DirectoryNotFoundError:
            return "Directory is already deleted or never been in system"

        if found_directory.project.value != found_project.id_:
            raise DirectoryNotInProjectError("Given directory is not in given project")

        if self._directory_service.is_root(found_directory):
            raise AccessDeniedError("Cannot delete root directory")

        await self._directory_commands.delete(found_directory.id_)
        return "Dirctory deleted"
