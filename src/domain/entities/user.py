__all__ = ["User", "UserId"]


from datetime import date
from dataclasses import dataclass, field

from .base import Entity
from ..value_objects import Name, Uuid4, BirthDate


class UserId(Uuid4): 
    def __hash__(self):
        return hash(self.value)

@dataclass
class User(Entity[UserId]):

    name: Name
    bio: str = ""
    birthdate: BirthDate = None
