from dataclasses import dataclass
from typing import Sequence, TypedDict

from domain.entities import ProjectGroupId, ProjectId, User, UserId
from domain.enums import ProjectRole
from domain.value_objects import Name

from application.ports.authorization import (
    CanManageProjectContent,
    ProjectContentManagmentContext,
    authorize,
)
from application.ports.gateways import UserQueryGateway
from application.ports.gateways.query_params import UserListParams
from application.services import ProjectGroupManageContextService


@dataclass
class ListProjectGroupMembersRequest:
    project_id: ProjectId
    group_id: ProjectGroupId

    @classmethod
    def from_primitives(
        cls,
        project_id: str,
        group_id: str,
    ) -> "ListProjectGroupMembersRequest":
        return cls(
            project_id=ProjectId(project_id),
            group_id=ProjectGroupId(group_id),
        )


class ListProjectGroupMembersElementResponse(TypedDict):
    user_id: UserId
    name: Name
    bio: str
    role: ProjectRole

    @classmethod
    def from_entity(
        cls,
        user: User,
        role: ProjectRole,
    ) -> "ListProjectGroupMembersElementResponse":
        return cls(
            user_id=user.id_,
            name=user.name,
            bio=user.bio,
            role=role,
        )


class ListProjectGroupMembersUsecase:
    def __init__(
        self,
        context_service: ProjectGroupManageContextService,
        user_queries: UserQueryGateway,
    ) -> None:
        self._context_service = context_service
        self._user_queries = user_queries

    async def __call__(
        self,
        request: ListProjectGroupMembersRequest,
        params: UserListParams,
    ) -> list[ListProjectGroupMembersElementResponse]:
        context = await self._context_service(request.project_id, request.group_id)

        authorize(
            CanManageProjectContent(),
            context=ProjectContentManagmentContext(
                subject=context.current_user,
                target=context.pinned_project,
            ),
        )

        users: Sequence[User] = await self._user_queries.by_ids(
            [participant.value for participant in context.found_group.participants],
            params,
        )
        project_members = context.pinned_project.members

        return [
            ListProjectGroupMembersElementResponse.from_entity(
                user=user,
                role=project_members.get(UserId(user.id_)),
            )
            for user in users
        ]
