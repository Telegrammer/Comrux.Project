__all__ = ["ProjectCommandGateway", "ProjectQueryGateway"]

from abc import abstractmethod
from typing import Protocol, Sequence

from domain import Project, ProjectId, UserId
from domain.value_objects import Name
from domain.enums import ProjectRole
from .query_params import ProjectListParams


class ProjectCommandGateway(Protocol):

    @abstractmethod
    async def add(self, project: Project) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, project: Project) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, obj) -> None:
        raise NotImplementedError


class ProjectQueryGateway(Protocol):

    @abstractmethod
    async def by_id(self, project_id: ProjectId) -> Project:
        raise NotImplementedError

    @abstractmethod
    async def read_all(self, params: ProjectListParams) -> Sequence[tuple[Project, Name]]:
        raise NotImplementedError

    @abstractmethod
    async def by_user(
        self, user_id: UserId, role: ProjectRole
    ) -> Sequence[tuple[Project, ProjectRole]]:
        raise NotImplementedError
