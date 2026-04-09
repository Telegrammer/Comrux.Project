from datetime import datetime
from typing import TypedDict
from dataclasses import dataclass

from domain.value_objects import FileName
from domain.enums import ProjectUnitAction
from domain.entities import ProjectId, DirectoryId, UserId, Directory, ProjectUnitId
from domain.entities.access_list import ResolvedUnitPermissions
from domain.services import DirectoryService
from application.ports import (
    DirectoryCommandGateway,
    Clock,
)
from application.services import (
    DirectoryManageContext,
    DirectoryManageContextService,
    ProjectUnitPermissionService,
)
from application.exceptions import (
    AccessDeniedError,
)


@dataclass
class CreateDirectoryRequest:
    project_id: ProjectId
    parent_id: DirectoryId
    name: FileName

    @classmethod
    def from_primitives(
        cls, project: str, parent: str, name: str
    ) -> "CreateDirectoryRequest":
        return cls(
            project_id=ProjectId(project),
            parent_id=DirectoryId(parent),
            name=FileName(name),
        )


class CreateDirectoryResponse(TypedDict):
    directory: DirectoryId
    created_by: UserId


class CreateDirectoryUsecase:
    def __init__(
        self,
        clock: Clock,
        context_service: DirectoryManageContextService,
        permission_service: ProjectUnitPermissionService,
        directory_service: DirectoryService,
        directory_commands: DirectoryCommandGateway,
    ):
        self._clock = clock
        self._context_service = context_service
        self._permission_service = permission_service
        self._directory_service: DirectoryService = directory_service
        self._directory_commands: DirectoryCommandGateway = directory_commands

    async def __call__(
        self, request: CreateDirectoryRequest
    ) -> CreateDirectoryResponse:
        now: datetime = self._clock.now()

        context: DirectoryManageContext = await self._context_service(
            request.project_id, request.parent_id
        )

        permissions: ResolvedUnitPermissions = await self._permission_service(
            context.current_user,
            context.pinned_project,
            ProjectUnitId(context.found_directory.id_),
        )

        if ProjectUnitAction.WRITE in permissions.denied:
            raise AccessDeniedError(
                "Cannot create directory. Parent directory have restrictions by acls"
            )

        new_directory: Directory = self._directory_service.create_directory(
            project=context.pinned_project,
            parent=context.found_directory,
            creator=UserId(context.current_user.id_),
            name=request.name,
            now=now,
        )

        await self._directory_commands.add(new_directory)
        return CreateDirectoryResponse(
            directory=new_directory.id_, created_by=context.current_user.id_
        )
