__all__ = ["AuthInfoPresenter"]


from typing import Protocol
from abc import abstractmethod, ABC
from application.usecases import CreateContentTicketResponse

from presentation.models import AuthInfo


class AuthInfoPresenter(ABC):

    @abstractmethod
    def to_auth_info[**P, T](
        self, raw_data: T, *args: P.args, **kwargs: P.kwargs
    ) -> AuthInfo:
        raise NotImplementedError

    def validate[**P, T](self, raw_data: T, *args: P.args, **kwargs: P.kwargs) -> bool:
        self.to_auth_info(raw_data, *args, **kwargs)
        return True


class ContentTicketPresenter(Protocol):

    @abstractmethod
    def present(self, payload: CreateContentTicketResponse) -> str:
        raise NotImplementedError
