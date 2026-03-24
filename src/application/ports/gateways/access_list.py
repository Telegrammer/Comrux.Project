from abc import abstractmethod
from typing import Protocol, Sequence
from domain.entities import AccessList, ProjectId, AccessListId, ProjectUnitId
from domain.value_objects import Name

from application.models import ProjectAccessListsRead
from .query_params import AccessListsParams


class AccessListCommandGateway(Protocol):

    @abstractmethod
    async def add(self, access_list: AccessList) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, access_list: AccessList) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, access_list: AccessList) -> None:
        raise NotImplementedError


class AccessListQueryGateway(Protocol):

    @abstractmethod
    async def by_project(
        self, project_id: ProjectId, params: AccessListsParams
    ) -> ProjectAccessListsRead:
        raise NotImplementedError

    @abstractmethod
    async def by_id(self, access_list_id: AccessListId) -> AccessList:
        raise NotImplementedError

    @abstractmethod
    async def by_project_unit(
        self, project_unit_id: ProjectUnitId
    ) -> Sequence[AccessList]:
        raise NotImplementedError
