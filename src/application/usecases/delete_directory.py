from dataclasses import dataclass
from typing import Sequence
from domain import Directory, ProjectId, User, Project, DirectoryId, ProjectUnitId
from domain.entities.access_list import ResolvedUnitPermissions
from domain.enums import ProjectUnitAction


from domain import DirectoryService
from application.ports import (
    ProjectQueryGateway,
    DirectoryCommandGateway,
    DirectoryQueryGateway,
)
from application.services import (
    CurrentUserService,
    DirectoryManageContext,
    DirectoryManageContextService,
    ProjectUnitPermissionService,
)
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
        context_service: DirectoryManageContextService,
        permission_service: ProjectUnitPermissionService,
        directory_commands: DirectoryCommandGateway,
        directory_service: DirectoryService,
    ):
        self._context_service = context_service
        self._permission_service = permission_service
        self._directory_commands: DirectoryCommandGateway = directory_commands
        self._directory_service: DirectoryService = directory_service

    async def __call__(self, request: DeleteDirectoryRequest) -> str:

        try:
            context = await self._context_service(
                request.project_id.value, request.directory_id.value
            )
        except DirectoryNotFoundError:
            return "Directory is already deleted or never been in system"

        if self._directory_service.is_root(context.found_directory):
            raise AccessDeniedError("Cannot delete root directory")

        permissions: ResolvedUnitPermissions = await self._permission_service(
            context.current_user,
            context.pinned_project,
            ProjectUnitId(context.found_directory.parent.value),
        )

        if ProjectUnitAction.WRITE in permissions.denied:
            raise AccessDeniedError(
                "Delete operation is restricted for parent directory"
            )

        deleted_units: Sequence[ProjectUnitId] | None = (
            await self._directory_commands.delete(context.found_directory.id_)
        )
        return "Dirctory deleted"
