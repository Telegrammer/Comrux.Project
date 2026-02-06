__all__ = [
    "ListCurrentUserProjectsRequest",
    "ListCurrentUserProjectsResponse",
    "ListCurrentUserProjectsUsecase",
]


from datetime import datetime
from dataclasses import dataclass
from typing import TypedDict, Sequence

from domain import Project, ProjectId, User
from domain.enums import ProjectRole
from domain.value_objects import Title, PassedDatetime
from application.ports.gateways import ProjectListParams, ProjectQueryGateway
from application.services import CurrentUserService


@dataclass
class ListCurrentUserProjectsRequest:

    role: ProjectRole
    search_params: ProjectListParams


class ListCurrentUserProjectsResponse(TypedDict):

    id_: ProjectId
    title: Title
    description: str
    role: ProjectRole
    created_at: PassedDatetime

    @classmethod
    def from_entity(
        cls, entity: Project, role: ProjectRole
    ) -> "ListCurrentUserProjectsResponse":
        return cls(
            id_=entity.id_,
            title=entity.title,
            description=entity.description,
            role=role,
            created_at=entity.created_at,
        )


class ListCurrentUserProjectsUsecase:

    def __init__(
        self,
        project_gateway: ProjectQueryGateway,
        current_user: CurrentUserService,
    ):
        self._project_gateway: ProjectQueryGateway = project_gateway
        self._current_user: CurrentUserService = current_user

    async def __call__(
        self,
        request: ListCurrentUserProjectsRequest,
    ) -> list[ListCurrentUserProjectsResponse]:

        current_user: User = await self._current_user()
        response: Sequence[tuple[Project, ProjectRole]] = (
            await self._project_gateway.by_user(
                current_user.id_, request.role, request.search_params
            )
        )
        return [
            ListCurrentUserProjectsResponse.from_entity(proj, role)
            for proj, role in response
        ]
