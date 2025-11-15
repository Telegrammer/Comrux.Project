__all__ = [
    "SortingOrder",
    "Pagination",
    "OffsetPagination",
    "CreationPagination",
    "SortingParam",
]

from enum import StrEnum
from datetime import datetime
from dataclasses import dataclass
from abc import ABC, abstractmethod

from domain.value_objects import Id


class SortingOrder(StrEnum):
    ascending = "ASC"
    descending = "DESC"


class Pagination: ...


@dataclass(frozen=True, slots=True)
class OffsetPagination(Pagination):
    offset: int
    limit: int


@dataclass(frozen=True, slots=True)
class CreationPagination(Pagination):
    latest_creation: datetime
    latest_id: Id
    limit: int


@dataclass(frozen=True, slots=True)
class SortingParam:
    field_name: str
    sorting_order: SortingOrder
