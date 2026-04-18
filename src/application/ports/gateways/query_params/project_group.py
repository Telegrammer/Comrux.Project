from enum import StrEnum
from dataclasses import dataclass

from .common import OffsetPagination, SearchQuery


class ProjectGroupFilterField(StrEnum):
    NAME = "name"
    IS_PUBLIC = "is_public"


@dataclass(frozen=True, slots=True)
class ProjectGroupListParams(SearchQuery[OffsetPagination]): ...
