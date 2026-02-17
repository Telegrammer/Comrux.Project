from abc import ABC, abstractmethod
from ...entities import ProjectUnitId


class ProjectUnitIdGenerator(ABC):

    @abstractmethod
    def __call__(self, *args, **kwds) -> ProjectUnitId:
        raise NotImplementedError
