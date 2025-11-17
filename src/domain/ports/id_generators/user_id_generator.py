__all__ = ["UserIdGenerator"]


from abc import ABC, abstractmethod
from domain.entities.user import UserId


class UserIdGenerator(ABC):

    @abstractmethod
    def __call__(self, *args, **kwds) -> UserId:
        raise NotImplementedError
