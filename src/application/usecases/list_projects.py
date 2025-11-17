__all__ = [
    "ListProjectsElementResponse",
    "ListProjectsUsecase",
]


from datetime import datetime
from typing import TypedDict, Sequence

from domain import Project, ProjectId
from domain.value_objects import Title, PassedDatetime
from application.ports.gateways import ProjectListParams, ProjectQueryGateway


class ListProjectsElementResponse(TypedDict):

    id_: ProjectId
    title: Title
    description: str
    created_at: PassedDatetime

    @classmethod
    def from_entity(cls, entity: Project) -> "ListProjectsElementResponse":
        return cls(
            id_=entity.id_,
            title=entity.title,
            description=entity.description,
            created_at=entity.created_at,
        )


class ListProjectsUsecase:

    def __init__(self, project_gateway: ProjectQueryGateway):
        self._project_gateway: ProjectQueryGateway = project_gateway

    async def __call__(
        self, search_request: ProjectListParams
    ) -> list[ListProjectsElementResponse]:
        response: list[Project] = await self._project_gateway.read_all(search_request)
        return [ListProjectsElementResponse.from_entity(elem) for elem in response]
