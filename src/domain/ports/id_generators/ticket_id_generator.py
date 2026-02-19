from abc import ABC, abstractmethod
from ...entities.content_ticket import ContentTicketId


class ContentTicketIdGenerator(ABC):

    @abstractmethod
    def __call__(self, *args, **kwds) -> ContentTicketId:
        raise NotImplementedError
