from __future__ import annotations
from typing import Protocol, TYPE_CHECKING, Sequence
from abc import abstractmethod

if TYPE_CHECKING:
    from ..entities import Document, Directory, ProjectUnit


class ProjectUnitVisitor(Protocol):

    @abstractmethod
    def visit_document[resT](self, document: Document) -> resT:
        raise NotImplementedError

    @abstractmethod
    def visit_directory[resT](self, directory: Directory) -> resT:
        raise NotImplementedError

    @abstractmethod
    def visit_sequence(self, units: Sequence[ProjectUnit]) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_visited[resT](self) -> list[resT]:
        raise NotImplementedError

    @abstractmethod
    def count_visited(self) -> int:
        raise NotImplementedError
