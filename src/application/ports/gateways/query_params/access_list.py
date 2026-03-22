from enum import StrEnum
from dataclasses import dataclass
from .common import OffsetPagination, SearchQuery


class AccessListFilterField(StrEnum):
    NAME = "name"
    OWNER = "owner"
    TARGET = "target"


@dataclass(frozen=True, slots=True)
class AccessListsParams(SearchQuery[OffsetPagination]): ...
