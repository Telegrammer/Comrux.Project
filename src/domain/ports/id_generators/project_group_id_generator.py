from abc import ABC, abstractmethod

from domain.entities import ProjectGroupId


class ProjectGroupIdGenerator(ABC):
    @abstractmethod
    def __call__(self, *args, **kwargs) -> ProjectGroupId:
        raise NotImplementedError
