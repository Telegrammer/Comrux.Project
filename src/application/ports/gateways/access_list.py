from abc import abstractmethod
from typing import Protocol, Sequence
from domain.entities import AccessList, ProjectId
from domain.value_objects import Name

from application.models import ProjectAccessListsRead
from .query_params import AccessListsParams


class AccessListCommandGateway(Protocol):

    @abstractmethod
    async def add(self, user: AccessList) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, user: AccessList) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, user: AccessList) -> None:
        raise NotImplementedError


class AccessListQueryGateway(Protocol):

    @abstractmethod
    async def by_project(
        self, project_id: ProjectId, params: AccessListsParams
    ) -> ProjectAccessListsRead:
        raise NotImplementedError
