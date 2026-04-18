__all__ = ["ProjectGroupCommandGateway", "ProjectGroupQueryGateway"]

from abc import abstractmethod
from typing import Protocol, Sequence

from domain.entities import ProjectGroup, ProjectGroupId, ProjectId, UserId

from .query_params import ProjectGroupListParams


class ProjectGroupCommandGateway(Protocol):
    @abstractmethod
    async def add(self, group: ProjectGroup) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, group: ProjectGroup) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, group: ProjectGroup) -> None:
        raise NotImplementedError


class ProjectGroupQueryGateway(Protocol):
    @abstractmethod
    async def by_id(self, group_id: ProjectGroupId) -> ProjectGroup:
        raise NotImplementedError

    @abstractmethod
    async def by_project(
        self, project_id: ProjectId, params: ProjectGroupListParams
    ) -> Sequence[ProjectGroup]:
        raise NotImplementedError

    @abstractmethod
    async def group_ids_for_user(
        self, project_id: ProjectId, user_id: UserId
    ) -> frozenset[ProjectGroupId]:
        raise NotImplementedError
