__all__ = ["UserListParams"]


from dataclasses import dataclass
from .common import SortingParam, OffsetPagination


@dataclass(frozen=True, slots=True)
class UserListParams:
    pagination: OffsetPagination
    sorting: list[SortingParam]