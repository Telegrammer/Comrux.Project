from dataclasses import dataclass


from ..value_objects import Uuid4, Title, PassedDatetime
from .base import Entity


class ProjectId(Uuid4): ...


@dataclass
class Project(Entity[ProjectId]):

    title: Title
    description: str = ""
    created_at: PassedDatetime

