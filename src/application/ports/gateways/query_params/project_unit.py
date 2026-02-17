from dataclasses import dataclass
from .common import SearchQuery, OffsetPagination


@dataclass(frozen=True, slots=True)
class ProjectUnitListParams(SearchQuery[OffsetPagination]): ...
