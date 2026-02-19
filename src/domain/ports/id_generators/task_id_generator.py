from abc import abstractmethod, ABC
from domain.entities.task import TaskId

__all__ = ["TaskIdGenerator"]


class TaskIdGenerator(ABC):

    @abstractmethod
    def __call__(self, *args, **kwargs) -> TaskId:
        raise NotImplementedError
