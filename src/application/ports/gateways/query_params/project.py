__all__ = ["ProjectListParams"]


from dataclasses import dataclass
from .common import OffsetPagination, SearchQuery


@dataclass(frozen=True, slots=True)
class ProjectListParams(SearchQuery[OffsetPagination]): ...
