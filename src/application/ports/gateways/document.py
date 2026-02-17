from abc import abstractmethod
from typing import Protocol, Sequence

from domain import Document, DocumentId


class DocumentCommandGateway(Protocol):

    @abstractmethod
    async def add(self, document: Document) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, document: Document) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, obj) -> None:
        raise NotImplementedError
