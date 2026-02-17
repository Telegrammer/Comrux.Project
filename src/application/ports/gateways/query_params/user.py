__all__ = ["UserListParams"]


from dataclasses import dataclass
from .common import SortingParam, OffsetPagination, SearchQuery


@dataclass(frozen=True, slots=True)
class UserListParams(SearchQuery[OffsetPagination]): ...
