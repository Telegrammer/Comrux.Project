__all__ = [
    "ListProjectMembersRequest",
    "ListProjectMembersUsecase",
    "ListProjectMembersElementResponse",
]


from dataclasses import dataclass
from typing import TypedDict, Sequence


from domain import Project, ProjectId, User, UserId
from domain.enums import ProjectRole
from domain.value_objects import Name

from application.ports import ProjectQueryGateway, UserQueryGateway, UserListParams
from application.exceptions import (
    ProjectNotFoundError,
)


@dataclass
class ListProjectMembersRequest:

    project_id: ProjectId

    @classmethod
    def from_primitives(cls, project_id: str) -> "ListProjectMembersRequest":
        return cls(project_id=ProjectId(project_id))


class ListProjectMembersElementResponse(TypedDict):

    user_id: UserId
    name: Name
    bio: str
    role: ProjectRole

    @classmethod
    def from_entity(
        cls, user: User, role: ProjectRole
    ) -> "ListProjectMembersElementResponse":
        return cls(user_id=user.id_, name=user.name, bio=user.bio, role=role)


class ListProjectMembersUsecase:

    def __init__(
        self,
        project_gateway: ProjectQueryGateway,
        user_gateway: UserQueryGateway,
    ):
        self._project_gateway = project_gateway
        self._user_gateway = user_gateway

    async def __call__(
        self, request: ListProjectMembersRequest, search_params: UserListParams
    ) -> list[ListProjectMembersElementResponse]:

        found_project: Project = await self._project_gateway.by_id(
            request.project_id.value
        )
        if not found_project:
            raise ProjectNotFoundError("Project with given id does not exist")

        members: dict[UserId, ProjectRole] = found_project.members
        users: Sequence[User] = await self._user_gateway.by_ids(
            [elem.value for elem in members.keys()], search_params
        )

        response: list[ListProjectMembersElementResponse] = []
        for user in users:
            response.append(
                ListProjectMembersElementResponse.from_entity(
                    user, members.get(getattr(user, "__object_id_"))
                )
            )
        return response
