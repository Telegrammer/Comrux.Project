__all__ = ["ProjectCommandGateway", "ProjectQueryGateway"]

from abc import abstractmethod
from typing import Protocol, Sequence
from functools import singledispatchmethod

from domain import Project, ProjectId
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
    async def read_all(self, params: ProjectListParams) -> Sequence[Project]:
        raise NotImplementedError
