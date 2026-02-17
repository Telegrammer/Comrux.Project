__all__ = ["CreateProjectRequest", "CreateProjectUsecase", "CreateProjectResponse"]


from datetime import datetime
from typing import TypedDict
from dataclasses import dataclass


from domain.value_objects import Title
from domain.entities import Project, ProjectId, User, UserId, DirectoryId, Directory
from domain.services import ProjectService, DirectoryService
from application.ports import ProjectCommandGateway, Clock, DirectoryCommandGateway
from application.services import CurrentUserService


@dataclass
class CreateProjectRequest:

    title: Title
    description: str

    @classmethod
    def from_primitives(cls, title: str, description: str) -> "CreateProjectRequest":
        return cls(Title(title), description)


class CreateProjectResponse(TypedDict):
    project_id: ProjectId
    root_directory_id: DirectoryId

    @classmethod
    def from_entity(
        cls, project: Project, directory: Directory
    ) -> "CreateProjectResponse":
        return cls(project_id=project.id_, root_directory_id=directory.id_)


class CreateProjectUsecase:

    def __init__(
        self,
        current_user_service: CurrentUserService,
        project_service: ProjectService,
        project_gateway: ProjectCommandGateway,
        directory_service: DirectoryService,
        directory_gateway: DirectoryCommandGateway,
        clock: Clock,
    ):
        self._current_user: CurrentUserService = current_user_service
        self._project_service: ProjectService = project_service
        self._project_gateway: ProjectCommandGateway = project_gateway
        self._directory_service: DirectoryService = directory_service
        self._directory_gateway: DirectoryCommandGateway = directory_gateway
        self._clock: Clock = clock

    async def __call__(self, request: CreateProjectRequest) -> CreateProjectResponse:

        now: datetime = self._clock.now()
        current_user: User = await self._current_user()
        new_project: Project = self._project_service.create_project(
            title=request.title,
            description=request.description,
            owner=current_user.id_,
            now=now,
        )
        root_directory: Directory = self._directory_service.create_root_directory(
            new_project, UserId(current_user.id_), now
        )

        await self._project_gateway.add(new_project)
        await self._directory_gateway.add(root_directory)
        return CreateProjectResponse.from_entity(new_project, root_directory)
