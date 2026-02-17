from __future__ import annotations
from typing import Protocol, TYPE_CHECKING
from abc import abstractmethod


if TYPE_CHECKING:
    from .common import OffsetPagination, CreationPagination, NamePagination


class PaginationVisitor[T](Protocol):

    @abstractmethod
    def visit_offset(self, pagination: OffsetPagination) -> T:
        raise NotImplementedError

    @abstractmethod
    def visit_created_at(self, pagination: CreationPagination) -> T:
        raise NotImplementedError

    @abstractmethod
    def visit_name(self, pagination: NamePagination) -> T:
        raise NotImplementedError
