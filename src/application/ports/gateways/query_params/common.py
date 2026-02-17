from __future__ import annotations
from typing import TYPE_CHECKING
from abc import abstractmethod
from enum import StrEnum
from datetime import datetime
from dataclasses import dataclass

from domain.value_objects import Id, FileName, Name

if TYPE_CHECKING:
    from .pagination_visitor import PaginationVisitor


class SortingOrder(StrEnum):
    ASCENDING = "ASC"
    DESCENDING = "DESC"


class Pagination:

    @abstractmethod
    def accept[T](self, visitor: PaginationVisitor) -> T:
        raise NotImplementedError


@dataclass(frozen=True, slots=True)
class OffsetPagination(Pagination):
    offset: int
    limit: int

    def accept[T](self, visitor: PaginationVisitor) -> T:
        return visitor.visit_offset(self)


@dataclass(frozen=True, kw_only=True)
class CursorPagination(Pagination):
    latest_id: Id | None
    limit: int


@dataclass(frozen=True, slots=True)
class CreationPagination(CursorPagination):
    latest_creation: datetime | None

    def accept[T](self, visitor: PaginationVisitor) -> T:
        return visitor.visit_created_at(self)


@dataclass(frozen=True, slots=True)
class NamePagination(CursorPagination):
    latest_name: FileName | Name | None

    def accept[T](self, visitor: PaginationVisitor) -> T:
        return visitor.visit_name(self)


@dataclass(frozen=True, slots=True)
class SortingParam:
    field_name: str
    sorting_order: SortingOrder


@dataclass(frozen=True)
class SearchQuery[pagT: Pagination]:
    pagination: pagT
    sorting: list[SortingParam]
