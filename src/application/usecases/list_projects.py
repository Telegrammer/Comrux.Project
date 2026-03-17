__all__ = [
    "ListProjectsElementResponse",
    "ListProjectsUsecase",
]


from datetime import datetime
from typing import TypedDict, Sequence

from domain import Project, ProjectId, UserId, DirectoryId, User
from domain.services import ProjectService
from domain.value_objects import Title, PassedDatetime, Name
from application.ports.gateways import (
    ProjectListParams,
    ProjectQueryGateway,
    UserQueryGateway,
)


class ListProjectsElementResponse(TypedDict):

    id_: ProjectId
    title: Title
    description: str
    owner_id: UserId
    owner_name: Name
    members_count: int
    created_at: PassedDatetime
    root_id: DirectoryId

    @classmethod
    def from_entity(
        cls,
        entity: Project,
        owner: User,
    ) -> "ListProjectsElementResponse":
        return cls(
            id_=entity.id_,
            title=entity.title,
            description=entity.description,
            owner_id=owner.id_,
            owner_name=owner.name,
            members_count=len(entity.members),
            created_at=entity.created_at,
            root_id=entity.root_directory,
        )


class ListProjectsUsecase:

    def __init__(
        self,
        project_serivce: ProjectService,
        project_gateway: ProjectQueryGateway,
        user_gateway: UserQueryGateway,
    ):
        self._project_service: ProjectService = project_serivce
        self._project_gateway: ProjectQueryGateway = project_gateway
        self._user_gateway: UserQueryGateway = user_gateway

    async def __call__(
        self, search_request: ProjectListParams
    ) -> list[ListProjectsElementResponse]:
        projects: Sequence[Project] = await self._project_gateway.read_all(
            search_request
        )

        unique_owner_ids: list[UserId] = {
            self._project_service.get_owner_id(proj).value for proj in projects
        }

        owners: Sequence[User] = await self._user_gateway.by_ids(unique_owner_ids)
        owners_map: dict[UserId, User] = {owner.id_: owner for owner in owners}

        return [
            ListProjectsElementResponse.from_entity(
                proj, owners_map[self._project_service.get_owner_id(proj).value]
            )
            for proj in projects
        ]
