__all__ = ["ProjectId", "Project"]


from dataclasses import dataclass, field


from .base import Entity
from .user import UserId
from ..value_objects import Uuid4, Title, PassedDatetime
from ..enums import ProjectRole


class ProjectId(Uuid4): ...


@dataclass
class Project(Entity[ProjectId]):

    title: Title
    description: str = ""
    members: dict[UserId, ProjectRole] = field(default_factory=dict)
    created_at: PassedDatetime
