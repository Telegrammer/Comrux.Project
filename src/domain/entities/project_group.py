__all__ = ["ProjectGroupId", "ProjectGroup"]

from dataclasses import dataclass, field

from .base import AggregationRoot
from .project import ProjectId
from .user import UserId
from ..value_objects import Color, Title, Uuid4


class ProjectGroupId(Uuid4): ...


@dataclass
class ProjectGroup(AggregationRoot[ProjectGroupId]):
    project_id: ProjectId
    name: Title
    color: Color
    owner: UserId
    participants: list[UserId] = field(default_factory=list)
    is_public: bool = False
