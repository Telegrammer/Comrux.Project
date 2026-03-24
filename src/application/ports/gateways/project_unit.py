from abc import abstractmethod
from typing import Protocol, Sequence

from domain import ProjectUnit, DirectoryId
from .query_params import ProjectUnitListParams


class ProjectUnitCommandGateway(Protocol):

    @abstractmethod
    async def update(self, unit: ProjectUnit) -> None:
        raise NotImplementedError


class ProjectUnitQueryGateway(Protocol):

    @abstractmethod
    async def by_directory(
        self, directory_id: DirectoryId, params: ProjectUnitListParams
    ) -> Sequence[ProjectUnit]:
        raise NotImplementedError
