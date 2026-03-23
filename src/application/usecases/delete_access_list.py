from dataclasses import dataclass
from domain.entities import ProjectId, AccessListId, User, Project, AccessList
from domain.services import ProjectService

from application.exceptions import AccessListNotInProjectError, AccessListNotFoundError
from application.ports.authorization import (
    authorize,
    AccessListManagmentContext,
    CanDeleteAccessList,
)
from application.ports.gateways import (
    ProjectQueryGateway,
    AccessListQueryGateway,
    AccessListCommandGateway,
)
from application.services import CurrentUserService


@dataclass
class DeleteAccessListRequest:

    project_id: ProjectId
    access_list_id: AccessListId

    @classmethod
    def from_primitives(
        cls, project_id: str, access_list_id: str
    ) -> "DeleteAccessListRequest":
        return cls(
            project_id=ProjectId(project_id),
            access_list_id=AccessListId(access_list_id),
        )


class DeleteAccessListUsecase:

    def __init__(
        self,
        project_queries: ProjectQueryGateway,
        project_service: ProjectService,
        current_user: CurrentUserService,
        acl_queries: AccessListQueryGateway,
        acl_commands: AccessListCommandGateway,
    ):
        self._project_queries = project_queries
        self._project_service = project_service
        self._current_user = current_user
        self._acl_queries = acl_queries
        self._acl_commands = acl_commands

    async def __call__(self, request: DeleteAccessListRequest) -> None:

        current_user: User = await self._current_user()
        found_project: Project = await self._project_queries.by_id(
            request.project_id.value
        )
        try:
            access_list: AccessList = await self._acl_queries.by_id(
                request.access_list_id.value
            )
        except AccessListNotFoundError:
            return

        if access_list.project != found_project.id_:
            raise AccessListNotInProjectError(
                "Given access list does not belongs to given project"
            )

        authorize(
            CanDeleteAccessList(),
            context=AccessListManagmentContext(
                subject=current_user,
                target_project=found_project,
                target_list=access_list,
            ),
        )

        await self._acl_commands.delete(access_list)
