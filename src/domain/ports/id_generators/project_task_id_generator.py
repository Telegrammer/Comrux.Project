from abc import ABC, abstractmethod

from domain.entities import ProjectTaskId


class ProjectTaskIdGenerator(ABC):
    @abstractmethod
    def __call__(self) -> ProjectTaskId:
        raise NotImplementedError
