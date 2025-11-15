__all__ = ["CreateProjectRequest", "CreateProjectUsecase", "CreateProjectResponse"]


from datetime import datetime
from typing import TypedDict
from dataclasses import dataclass


from domain.value_objects import Title
from domain.entities import Project, ProjectId
from domain.services import ProjectService
from application.ports import ProjectCommandGateway, Clock


@dataclass
class CreateProjectRequest:

    title: Title
    description: str

    @classmethod
    def from_primitives(cls, title: str, description: str) -> "CreateProjectRequest":
        return cls(Title(title), description)


class CreateProjectResponse(TypedDict):
    project_id: ProjectId

    @classmethod
    def from_entity(cls, entity: Project) -> "CreateProjectResponse":
        return cls(project_id=entity.id_)


class CreateProjectUsecase:

    def __init__(
        self,
        project_service: ProjectService,
        project_gateway: ProjectCommandGateway,
        clock: Clock,
    ):
        self._project_service = project_service
        self._project_gateway = project_gateway
        self._clock = clock

    async def __call__(self, request: CreateProjectRequest) -> CreateProjectResponse:

        now: datetime = self._clock.now()
        new_project: Project = self._project_service.create_project(
            title=request.title,
            description=request.description,
            now=now,
        )

        await self._project_gateway.add(new_project)
        return CreateProjectResponse.from_entity(new_project)
