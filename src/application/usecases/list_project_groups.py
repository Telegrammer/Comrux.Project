from dataclasses import dataclass
from typing import TypedDict

from domain.entities import Project, ProjectGroup, ProjectGroupId, ProjectId, User, UserId
from domain.value_objects import Color, Title


from application.ports.authorization import (
    CanManageProjectContent,
    ProjectContentManagmentContext,
    authorize,
)
from application.ports.gateways import (
    ProjectGroupQueryGateway,
    ProjectQueryGateway,
)
from application.ports.gateways.query_params import ProjectGroupListParams
from application.services import CurrentUserService


@dataclass
class ListProjectGroupsRequest:
    project_id: ProjectId

    @classmethod
    def from_primitives(cls, project_id: str) -> "ListProjectGroupsRequest":
        return cls(project_id=ProjectId(project_id))


class ListProjectGroupsElementResponse(TypedDict):
    id_: ProjectGroupId
    name: Title
    color: Color
    owner: UserId
    is_public: bool
    participants_count: int

    @classmethod
    def from_entity(
        cls,
        group: ProjectGroup,
    ) -> "ListProjectGroupsElementResponse":
        return cls(
            id_=group.id_,
            name=group.name,
            color=group.color,
            owner=group.owner,
            is_public=group.is_public,
            participants_count=len(group.participants),
        )


class ListProjectGroupsUsecase:
    def __init__(
        self,
        current_user: CurrentUserService,
        project_queries: ProjectQueryGateway,
        group_queries: ProjectGroupQueryGateway,
    ) -> None:
        self._current_user = current_user
        self._project_queries = project_queries
        self._group_queries = group_queries

    async def __call__(
        self,
        request: ListProjectGroupsRequest,
        params: ProjectGroupListParams,
    ) -> list[ListProjectGroupsElementResponse]:
        current_user: User = await self._current_user()
        project: Project = await self._project_queries.by_id(request.project_id.value)

        authorize(
            CanManageProjectContent(),
            context=ProjectContentManagmentContext(
                subject=current_user,
                target=project,
            ),
        )

        groups = await self._group_queries.by_project(project.id_, params)
        return [ListProjectGroupsElementResponse.from_entity(group) for group in groups]
