__all__ = ["User", "UserId"]


from datetime import date
from dataclasses import dataclass, field

from .base import Entity
from ..value_objects import Name, Uuid4, BirthDate, EmailAddress


class UserId(Uuid4):
    pass

@dataclass
class User(Entity[UserId]):

    name: Name
    bio: str = ""
    email: EmailAddress = None
    birthdate: BirthDate = None
