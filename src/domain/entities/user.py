__all__ = ["User", "UserId"]


from datetime import date
from dataclasses import dataclass, field

from .project import Project
from .base import Entity
from ..value_objects import Name, Uuid4, BirthDate


class UserId(Uuid4): ...


@dataclass
class User(Entity[UserId]):

    name: Name
    bio: str = ""
    birthdate: BirthDate = None
    projects: list[Project] = field(default_factory=list)
