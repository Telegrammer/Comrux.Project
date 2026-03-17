from datetime import date
from pydantic import BaseModel


class UserCreate(BaseModel):

    name: str
    bio: str
    birthdate: date | None


class UserCreated(BaseModel):
    user_id: str


class UserRead(UserCreate): ...


class UserSearchRead(BaseModel):
    id_: str
    name: str
    email: str | None
    bio: str = ""
