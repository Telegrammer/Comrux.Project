from abc import abstractmethod, ABC
from domain.entities.access_list import AccessListId


class AccessListIdGenerator(ABC):

    @abstractmethod
    def __call__(self, *args, **kwargs) -> AccessListId:
        raise NotImplementedError
