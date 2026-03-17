from typing import Sequence, TypedDict
from dataclasses import dataclass
from domain.entities import DirectoryId, ProjectId, ProjectUnit, Directory, UserId, User
from domain.ports import ProjectUnitVisitor
from application.ports import (
    DirectoryQueryGateway,
    ProjectUnitQueryGateway,
    UserQueryGateway,
)
from application.ports.gateways.query_params import ProjectUnitListParams
from application.exceptions import DirectoryNotInProjectError


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
        directory_gateway: DirectoryQueryGateway,
        project_unit_gateway: ProjectUnitQueryGateway,
        user_gateway: UserQueryGateway,
    ):
        self._directory_gateway: DirectoryQueryGateway = directory_gateway
        self._project_unit_gateway: ProjectUnitQueryGateway = project_unit_gateway
        self._user_gateway = user_gateway

    async def __call__(
        self,
        response_visitor: ProjectUnitVisitor,
        request: ListDirectoryContentRequest,
        search_params: ProjectUnitListParams,
    ) -> None:

        found_directory: Directory = await self._directory_gateway.by_id(
            request.parent_id.value
        )

        if found_directory.project != request.project_id:
            raise DirectoryNotInProjectError(
                "Directory with given id don't belong to given project"
            )

        units: Sequence[ProjectUnit] = await self._project_unit_gateway.by_directory(
            found_directory.id_, search_params
        )

        owner_ids: set[UserId] = {unit.created_by.value for unit in units}
        owners: Sequence[User] = await self._user_gateway.by_ids(owner_ids)

        response_visitor.visit_sequence(
            units, {UserId(owner.id_): owner for owner in owners}
        )
