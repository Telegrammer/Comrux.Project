from __future__ import annotations
from typing import TYPE_CHECKING
from abc import ABC, abstractmethod
from enum import StrEnum
from datetime import datetime
from dataclasses import dataclass

from domain.value_objects import Id, FileName, Name

if TYPE_CHECKING:
    from .pagination_visitor import PaginationVisitor
    from .filter_visitor import FilterVisitor


class SortingOrder(StrEnum):
    ASCENDING = "ASC"
    DESCENDING = "DESC"


class Pagination(ABC):

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


class FilterParam(ABC):
    field_name: str

    @abstractmethod
    def accept[T](self, visitor: FilterVisitor) -> T:
        raise NotImplementedError


@dataclass(frozen=True, slots=True)
class EqFilter[valT](FilterParam):
    field_name: str
    value: valT

    def accept[T](self, visitor: FilterVisitor) -> T:
        return visitor.visit_eq(self)


@dataclass(frozen=True, slots=True)
class InFilter[valT](FilterParam):
    field_name: str
    values: list[valT]

    def accept[T](self, visitor: FilterVisitor) -> T:
        return visitor.visit_in(self)


@dataclass(frozen=True, slots=True)
class RangeFilter[valT](FilterParam):
    field_name: str
    value_from: valT | None = None
    value_to: valT | None = None

    def accept[T](self, visitor: FilterVisitor) -> T:
        return visitor.visit_range(self)


@dataclass(frozen=True, slots=True)
class LikeFilter(FilterParam):

    field_name: str
    value: str
        
    def accept[T](self, visitor: FilterVisitor) -> T:
        return visitor.visit_like(self)


@dataclass(frozen=True, slots=True)
class OrFilter(FilterParam):
    filters: list[FilterParam]

    def accept[T](self, visitor: FilterVisitor) -> T:
        return visitor.visit_or(self)


@dataclass(frozen=True)
class SearchQuery[pagT: Pagination]:
    filters: list[FilterParam]
    pagination: pagT
    sorting: list[SortingParam]
