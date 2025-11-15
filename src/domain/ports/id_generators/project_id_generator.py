__all__ = ["ProjectIdGenerator"]


from abc import ABC, abstractmethod
from domain.entities.project import ProjectId

class ProjectIdGenerator(ABC):

    @abstractmethod
    def __call__(self, *args, **kwds) -> ProjectId:
        raise NotImplementedError