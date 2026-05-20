from typing import TypedDict

from domain.value_objects import FileName, Name
from domain.entities import (
    AccessList,
    AccessListId,
    AccessRule,
    UserId,
    ProjectId,
    Project,
)
from domain.entities.project_group import ProjectGroupId


from application.models import ProjectAccessListsRead
from application.ports.gateways import ProjectQueryGateway, AccessListQueryGateway
from application.ports.gateways.query_params import AccessListsParams
from dataclasses import dataclass


@dataclass
class ListProjectAccessListsRequest:
    project_id: ProjectId

    @classmethod
    def from_primitives(cls, project_id: str) -> "ListProjectAccessListsRequest":
        return cls(project_id=ProjectId(project_id))


class ListProjectAccessListsElementResponse(TypedDict):
    id_: AccessListId
    name: FileName
    owner_id: UserId
    owner_name: Name
    rules: list[AccessRule]

    @classmethod
    def from_entity(
        cls, entity: AccessList, owner: Name
    ) -> "ListProjectAccessListsElementResponse":
        return cls(
            id_=entity.id_,
            name=entity.name,
            owner_id=entity.owner,
            owner_name=owner.value,
            rules=entity.rules,
        )


class ListProjectAccessListResponse(TypedDict):
    access_lists: list[ListProjectAccessListsElementResponse]
    user_responsibles: dict[UserId, Name]
    group_responsibles: dict[ProjectGroupId, Name]


class ListAccessListsUsecase:
    def __init__(
        self, project_queries: ProjectQueryGateway, acl_queries: AccessListQueryGateway
    ):
        self._project_queries = project_queries
        self._acl_queries = acl_queries

    async def __call__(
        self, request: ListProjectAccessListsRequest, search_params: AccessListsParams
    ) -> ListProjectAccessListResponse:

        found_project: Project = await self._project_queries.by_id(
            request.project_id.value
        )

        access_lists_info: ProjectAccessListsRead = await self._acl_queries.by_project(
            found_project.id_, search_params
        )

        return ListProjectAccessListResponse(
            access_lists=[
                ListProjectAccessListsElementResponse.from_entity(acl, owner)
                for acl, owner in zip(
                    access_lists_info.access_lists, access_lists_info.owners
                )
            ],
            user_responsibles=access_lists_info.user_responsibles,
            group_responsibles=access_lists_info.group_responsibles,
        )
