from typing import TypedDict
from dataclasses import dataclass


from domain.value_objects import FileName, Name
from domain.entities import (
    ProjectId,
    AccessListId,
    UserId,
    User,
    AccessList,
    Project,
    AccessRule,
)
from domain.services import AccessListService


from application.services import CurrentUserService
from application.ports.gateways import AccessListCommandGateway, ProjectQueryGateway
from application.ports.authorization import (
    authorize,
    CanUpdateProject,
    ProjectManagmentContext,
)


@dataclass
class CreateAccessListRequest:

    name: FileName
    project_id: ProjectId

    @classmethod
    def from_primitives(cls, name: str, project_id: str) -> "CreateAccessListRequest":

        return cls(
            name=FileName(name),
            project_id=ProjectId(project_id),
        )


class CreateAccessListResponse(TypedDict):

    access_list_id: AccessListId
    owner_id: UserId
    owner_name: Name

    @classmethod
    def from_entity(cls, user: User, acl: AccessList) -> "CreateAccessListResponse":
        return cls(
            access_list_id=acl.id_,
            owner_id=user.id_,
            owner_name=user.name,
        )


class CreateAccessListUsecase:

    def __init__(
        self,
        current_user: CurrentUserService,
        project_queries: ProjectQueryGateway,
        acl_service: AccessListService,
        acl_commands: AccessListCommandGateway,
    ):
        self._current_user = current_user
        self._project_queries = project_queries
        self._acl_service = acl_service
        self._acl_commands = acl_commands

    async def __call__(
        self,
        request: CreateAccessListRequest,
        rules: list[AccessRule],
    ) -> CreateAccessListResponse:

        current_user: User = await self._current_user()
        found_project: Project = await self._project_queries.by_id(
            request.project_id.value
        )

        authorize(
            CanUpdateProject(),
            context=ProjectManagmentContext(subject=current_user, target=found_project),
        )

        access_list: AccessList = self._acl_service.create_access_list(
            request.name, current_user, found_project, rules
        )

        await self._acl_commands.add(access_list)

        return CreateAccessListResponse.from_entity(current_user, access_list)
