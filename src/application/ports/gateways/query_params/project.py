__all__ = ["ProjectListParams"]


from dataclasses import dataclass
from .common import SortingParam, OffsetPagination


@dataclass(frozen=True, slots=True)
class ProjectListParams:
    pagination: OffsetPagination
    sorting: list[SortingParam]
