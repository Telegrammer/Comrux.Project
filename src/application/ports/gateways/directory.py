__all__ = ["DirectoryCommandGateway", "DirectoryQueryGateway"]

from abc import abstractmethod
from typing import Protocol, Sequence

from domain import DirectoryId, Directory


class DirectoryCommandGateway(Protocol):

    @abstractmethod
    async def add(self, directory: Directory) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, directory: Directory) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, obj) -> None:
        raise NotImplementedError


class DirectoryQueryGateway(Protocol):

    @abstractmethod
    async def by_id(self, directory_id: DirectoryId) -> Directory:
        raise NotImplementedError
