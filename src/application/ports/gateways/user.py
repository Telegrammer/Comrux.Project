__all__ = ["UserCommandGateway", "UserQueryGateway"]


from abc import abstractmethod
from typing import Protocol, Sequence, Iterable

from domain import User, UserId

from application.ports.gateways.query_params import UserListParams


class UserCommandGateway(Protocol):

    @abstractmethod
    async def add(self, user: User) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, user: User) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, user: User) -> None:
        raise NotImplementedError


class UserQueryGateway(Protocol):

    @abstractmethod
    async def read_all(self, params: UserListParams) -> Sequence[User]:
        raise NotImplementedError

    @abstractmethod
    async def by_id(self, user_id: UserId) -> User | None:
        raise NotImplementedError

    @abstractmethod
    async def by_ids(self, ids: Iterable[UserId], params: UserListParams) -> Sequence[User]:
        raise NotImplementedError
