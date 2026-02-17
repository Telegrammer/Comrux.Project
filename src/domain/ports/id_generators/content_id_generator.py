__all__ = ["ContentIdGenerator"]


from abc import ABC, abstractmethod
from ...entities.document import ContentId


class ContentIdGenerator(ABC):

    @abstractmethod
    def __call__(self, *args, **kwds) -> ContentId:
        raise NotImplementedError
