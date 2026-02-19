from typing import TypedDict
from datetime import datetime
from application.usecases import CreateContentTicketResponse
from .base import ContentTicketPresenter
import jwt


class ContentTicketPayload(TypedDict):

    jti: str
    usr: str
    sub: str
    ref: str
    perms: list[str]
    iat: datetime
    exp: datetime


class JwtContentTicketPresenter(ContentTicketPresenter):

    def __init__(self, algorithm: str, private_key: str):
        self._private_key = private_key
        self._algorithm = algorithm

    def present(self, response: CreateContentTicketResponse) -> str:
        payload: ContentTicketPayload = ContentTicketPayload(
            jti=response["ticket_id"],
            usr=response["username"],
            sub=response["user_id"],
            ref=response["content_ref"],
            perms=response["permissions"],
            iat=response["issued_at"],
            exp=response["expire_at"],
        )
        return jwt.encode(
            payload=payload, key=self._private_key, algorithm=self._algorithm
        )
