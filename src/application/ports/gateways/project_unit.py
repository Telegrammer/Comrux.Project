from abc import abstractmethod
from typing import Protocol, Sequence

from domain import ProjectUnit, DirectoryId
from .query_params import ProjectUnitListParams


class ProjectUnitQueryGateway(Protocol):

    @abstractmethod
    async def by_directory(
        self, directory_id: DirectoryId, params: ProjectUnitListParams
    ) -> Sequence[ProjectUnit]:
        raise NotImplementedError
