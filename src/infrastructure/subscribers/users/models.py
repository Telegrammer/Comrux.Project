__all__ = ["UserCreated"]


from datetime import date
from pydantic import BaseModel


class UserCreated(BaseModel):

    user_id: str
    name: str
    bio: str
    birthdate: date

    model_config = {"extra": "ignore"}
