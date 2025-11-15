__all__ = [
    "ListProjectsElementResponse",
    "ListProjectsUsecase",
]


from datetime import datetime
from typing import TypedDict, Sequence

from domain import Project
from application.ports.gateways import ProjectListParams, ProjectQueryGateway


class ListProjectsElementResponse(TypedDict):

    title: str
    description: str
    created_at: datetime

    @classmethod
    def from_entity(cls, entity: Project) -> "ListProjectsElementResponse":
        return cls(
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
