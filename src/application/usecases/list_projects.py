__all__ = [
    "ListProjectsElementResponse",
    "ListProjectsUsecase",
]


from datetime import datetime
from typing import TypedDict, Sequence

from domain import Project, ProjectId, UserId
from domain.services import ProjectService
from domain.value_objects import Title, PassedDatetime
from application.ports.gateways import ProjectListParams, ProjectQueryGateway


class ListProjectsElementResponse(TypedDict):

    id_: ProjectId
    title: Title
    description: str
    owner_id: UserId
    members_count: int
    created_at: PassedDatetime

    @classmethod
    def from_entity(
        cls, entity: Project, owner: UserId
    ) -> "ListProjectsElementResponse":
        return cls(
            id_=entity.id_,
            title=entity.title,
            description=entity.description,
            owner_id=owner,
            members_count=len(entity.members),
            created_at=entity.created_at,
        )


class ListProjectsUsecase:

    def __init__(
        self,
        project_serivce: ProjectService,
        project_gateway: ProjectQueryGateway,
    ):
        self._project_service: ProjectService = project_serivce
        self._project_gateway: ProjectQueryGateway = project_gateway

    async def __call__(
        self, search_request: ProjectListParams
    ) -> list[ListProjectsElementResponse]:
        response: list[Project] = await self._project_gateway.read_all(search_request)
        return [
            ListProjectsElementResponse.from_entity(
                elem, self._project_service.get_owner_id(elem).value
            )
            for elem in response
        ]
