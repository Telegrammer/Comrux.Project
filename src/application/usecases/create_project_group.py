from dataclasses import dataclass
from typing import TypedDict

from domain.entities import ProjectGroup, ProjectGroupId, ProjectId, UserId
from domain.services import ProjectGroupService
from domain.value_objects import Color, HexColor, Title

from application.ports.authorization import (
    CanManageProjectGroup,
    ProjectGroupManagmentContext,
    authorize,
)
from application.ports.gateways import ProjectGroupCommandGateway, ProjectQueryGateway
from application.services import CurrentUserService


@dataclass
class CreateProjectGroupRequest:
    project_id: ProjectId
    name: Title
    color: Color
    is_public: bool
    participants: list[UserId]

    @classmethod
    def from_primitives(
        cls,
        project_id: str,
        name: str,
        color: str,
        is_public: bool,
        participants: list[str] | None = None,
    ) -> "CreateProjectGroupRequest":
        return cls(
            project_id=ProjectId(project_id),
            name=Title(name),
            color=HexColor(color),
            is_public=is_public,
            participants=[UserId(user_id) for user_id in participants or []],
        )


class CreateProjectGroupResponse(TypedDict):
    group_id: ProjectGroupId
    owner_id: UserId
    project_id: ProjectId

    @classmethod
    def from_entity(cls, group: ProjectGroup) -> "CreateProjectGroupResponse":
        return cls(
            group_id=group.id_,
            owner_id=group.owner,
            project_id=group.project_id,
        )


class CreateProjectGroupUsecase:
    def __init__(
        self,
        current_user: CurrentUserService,
        project_queries: ProjectQueryGateway,
        group_service: ProjectGroupService,
        group_commands: ProjectGroupCommandGateway,
    ) -> None:
        self._current_user = current_user
        self._project_queries = project_queries
        self._group_service = group_service
        self._group_commands = group_commands

    async def __call__(
        self, request: CreateProjectGroupRequest
    ) -> CreateProjectGroupResponse:
        current_user = await self._current_user()
        project = await self._project_queries.by_id(request.project_id.value)

        authorize(
            CanManageProjectGroup(),
            context=ProjectGroupManagmentContext(
                subject=current_user,
                target=project,
            ),
        )

        group = self._group_service.create_group(
            name=request.name,
            color=request.color,
            project=project,
            owner=UserId(current_user.id_),
            participants=request.participants,
            is_public=request.is_public,
        )
        await self._group_commands.add(group)

        return CreateProjectGroupResponse.from_entity(group)
