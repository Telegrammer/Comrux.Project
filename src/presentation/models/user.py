__all__ = ["UserCreate", "UserCreated"]


from datetime import date
from pydantic import BaseModel


class UserCreate(BaseModel):

    name: str
    bio: str
    birthdate: date | None


class UserCreated(BaseModel):
    user_id: str