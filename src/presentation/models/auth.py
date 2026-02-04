__all__ = ["AuthInfo", "JwtInfo", "SessionInfo", "PresentedAuthInfo"]


from pydantic import BaseModel
from datetime import datetime


class AuthInfo(BaseModel):
    key_id: str
    user_id: str | None = None
    created_at: datetime | None = None
    expire_at: datetime | None = None
