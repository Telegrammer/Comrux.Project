from enum import StrEnum
from dataclasses import dataclass
from domain.entities import UserId

from .common import SearchQuery, OffsetPagination


class ProjectTaskFilterField(StrEnum):
    STATUS = "status"


@dataclass(frozen=True, slots=True)
class ProjectTaskListParams(SearchQuery[OffsetPagination]):
    assigned_to_user_id: UserId | None = None
    mine: bool = False
