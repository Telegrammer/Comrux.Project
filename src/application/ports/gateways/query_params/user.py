__all__ = ["UserListParams"]


from enum import StrEnum
from dataclasses import dataclass
from .common import SortingParam, OffsetPagination, SearchQuery


class UserFilterField(StrEnum):
    NAME = "name"
    BIO = "bio"
    EMAIL = "email"


@dataclass(frozen=True, slots=True)
class UserListParams(SearchQuery[OffsetPagination]): ...
