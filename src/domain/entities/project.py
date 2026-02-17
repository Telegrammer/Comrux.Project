__all__ = ["ProjectId", "Project"]


from dataclasses import dataclass, field

from .base import AggregationRoot
from .user import UserId
from ..value_objects import Uuid4, Title, PassedDatetime
from ..enums import ProjectRole


class ProjectId(Uuid4): ...


@dataclass(kw_only=True)
class Project(AggregationRoot[ProjectId]):

    title: Title
    description: str = ""
    members: dict[UserId, ProjectRole] = field(default_factory=dict)
    created_at: PassedDatetime
