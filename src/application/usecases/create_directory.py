from datetime import datetime
from typing import TypedDict
from dataclasses import dataclass

from domain.value_objects import FileName
from domain.entities import ProjectId, DirectoryId, UserId, Directory
from domain.services import DirectoryService
from application.ports import (
    DirectoryCommandGateway,
    Clock,
)
from application.ports.authorization import (
    authorize,
    CanManageProjectContent,
    ProjectContentManagmentContext,
)
from application.services import (
    DirectoryManageContext,
    DirectoryManageContextService,
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
        directory_service: DirectoryService,
        directory_commands: DirectoryCommandGateway,
    ):
        self._clock = clock
        self._context_service = context_service
        self._directory_service: DirectoryService = directory_service
        self._directory_commands: DirectoryCommandGateway = directory_commands

    async def __call__(
        self, request: CreateDirectoryRequest
    ) -> CreateDirectoryResponse:
        now: datetime = self._clock.now()

        context: DirectoryManageContext = await self._context_service(
            request.project_id, request.parent_id
        )

        authorize(
            CanManageProjectContent(),
            context=ProjectContentManagmentContext(
                subject=context.current_user, target=context.pinned_project
            ),
        )
        new_directory: Directory = self._directory_service.create_directory(
            project=context.pinned_project,
            parent=context.parent_directory,
            creator=UserId(context.current_user.id_),
            name=request.name,
            now=now,
        )

        await self._directory_commands.add(new_directory)
        return CreateDirectoryResponse(
            directory=new_directory.id_, created_by=context.current_user.id_
        )
