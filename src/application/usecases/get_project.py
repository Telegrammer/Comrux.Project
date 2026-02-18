from dataclasses import dataclass
from typing import TypedDict
from domain import Project, ProjectId, DirectoryId, UserId
from domain.value_objects import Title, PassedDatetime
from domain.services import ProjectService
from application.ports import ProjectQueryGateway


class GetProjectRequest:

    project_id: ProjectId

    @classmethod
    def from_primitives(cls, project_id: str) -> "GetProjectRequest":
        return cls(project_id=ProjectId(project_id))


class GetProjectResponse(TypedDict):

    title: Title
    description: str
    owner: UserId
    creatad_at: PassedDatetime
    root_directory: DirectoryId

    @classmethod
    def from_entity(cls, project: Project, owner: UserId) -> "GetProjectResponse":

        return cls(
            title=project.title,
            description=project.description,
            owner=owner.value,
            created_at=project.created_at,
            root_directory=project.root_directory,
        )


class GetProjectService:

    def __init__(
        self, project_gateway: ProjectQueryGateway, project_service: ProjectService
    ):
        self._project_gateway: ProjectQueryGateway = project_gateway
        self._project_service: ProjectService = project_service

    async def __call__(self, request: GetProjectRequest) -> Project:
        found_project: Project = await self._project_gateway.by_id(
            request.project_id.value
        )
        return GetProjectResponse.from_entity(
            found_project, self._project_service.get_owner_id(found_project)
        )
