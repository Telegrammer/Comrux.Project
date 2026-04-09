from typing import Sequence
from dataclasses import dataclass
from domain.enums import ProjectUnitAction
from domain.entities.access_list import ResolvedUnitPermissions
from domain.entities import (
    DirectoryId,
    ProjectId,
    ProjectUnit,
    Directory,
    UserId,
    User,
    ProjectUnitId,
)
from domain.services import DirectoryService
from domain.ports import ProjectUnitVisitor
from application.ports import (
    DirectoryQueryGateway,
    ProjectUnitQueryGateway,
    UserQueryGateway,
    ProjectQueryGateway,
)
from application.ports.gateways.query_params import ProjectUnitListParams
from application.services import ProjectUnitPermissionService, CurrentUserService
from application.exceptions import DirectoryNotInProjectError, AccessDeniedError
from application.exceptions.user import CurrentUserNotAssignError


@dataclass
class ListDirectoryContentRequest:
    project_id: ProjectId
    parent_id: DirectoryId

    @classmethod
    def from_primitives(
        cls, project: str, parent: str
    ) -> "ListDirectoryContentRequest":
        return cls(project_id=ProjectId(project), parent_id=DirectoryId(parent))


class ListDirectoryContentUsecase:
    def __init__(
        self,
        directory_service: DirectoryService,
        directory_gateway: DirectoryQueryGateway,
        project_unit_gateway: ProjectUnitQueryGateway,
        project_queries: ProjectQueryGateway,
        permissions: ProjectUnitPermissionService,
        user_gateway: UserQueryGateway,
        current_user: CurrentUserService,
    ):
        self._directory_service = directory_service
        self._directory_gateway: DirectoryQueryGateway = directory_gateway
        self._project_unit_gateway: ProjectUnitQueryGateway = project_unit_gateway
        self._project_queries = project_queries
        self._user_gateway = user_gateway
        self._permissions = permissions
        self._current_user = current_user

    async def __call__(
        self,
        response_visitor: ProjectUnitVisitor,
        request: ListDirectoryContentRequest,
        search_params: ProjectUnitListParams,
    ) -> None:

        found_directory: Directory = await self._directory_gateway.by_id(
            request.parent_id.value
        )

        found_project = await self._project_queries.by_id(request.project_id.value)

        if not self._directory_service.belongs_to(found_directory, found_project):
            raise DirectoryNotInProjectError(
                "Directory with given id don't belong to given project"
            )

        try:
            current_user = await self._current_user()
            permissions: ResolvedUnitPermissions = await self._permissions(
                current_user, found_project, ProjectUnitId(found_directory.id_)
            )
        except CurrentUserNotAssignError:
            permissions = ResolvedUnitPermissions(
                allowed={}, denied={ProjectUnitAction.EXECUTE}
            )

        if ProjectUnitAction.EXECUTE in permissions.denied and found_project.is_private:
            raise AccessDeniedError(
                "Cannot list directory content because project's restrictions"
            )

        units: Sequence[ProjectUnit] = await self._project_unit_gateway.by_directory(
            found_directory.id_, search_params
        )

        owner_ids: set[UserId] = {unit.created_by.value for unit in units}
        owners: Sequence[User] = await self._user_gateway.by_ids(owner_ids)

        response_visitor.visit_sequence(
            units, {UserId(owner.id_): owner for owner in owners}
        )
