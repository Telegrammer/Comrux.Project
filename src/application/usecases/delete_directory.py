from dataclasses import dataclass
from typing import Sequence

from domain import DirectoryId, ProjectId, ProjectUnitId
from domain import DirectoryService
from domain.entities.access_list import ResolvedUnitPermissions
from domain.entities.document import ContentId
from domain.enums import ProjectUnitAction

from application.exceptions import AccessDeniedError, DirectoryNotFoundError
from application.ports import DirectoryCommandGateway
from application.services import (
    DirectoryManageContextService,
    ProjectUnitPermissionService,
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


@dataclass(frozen=True, slots=True)
class DeleteDirectoryResponse:
    project_id: ProjectId
    content_ids: tuple[ContentId, ...]
    deleted: bool
    message: str


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

    async def __call__(
        self, request: DeleteDirectoryRequest
    ) -> DeleteDirectoryResponse:

        try:
            context = await self._context_service(
                request.project_id.value, request.directory_id.value
            )
        except DirectoryNotFoundError:
            return DeleteDirectoryResponse(
                project_id=request.project_id,
                content_ids=(),
                deleted=False,
                message="Directory is already deleted or never been in system",
            )

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

        deleted_content: Sequence[ContentId] = await self._directory_commands.delete(
            context.found_directory.id_
        )
        return DeleteDirectoryResponse(
            project_id=request.project_id,
            content_ids=tuple(deleted_content),
            deleted=True,
            message="Directory deleted",
        )
