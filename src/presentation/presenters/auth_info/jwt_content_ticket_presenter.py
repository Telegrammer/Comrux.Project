from typing import TypedDict
from application.usecases import CreateContentTicketResponse
from .base import ContentTicketPresenter
import jwt


class BaseContentTicketPayload(TypedDict):
    jti: str
    usr: str
    sub: str
    ref: str
    grp: str
    perms: list[str]
    iat: float
    exp: float


class ContentTicketPayload(BaseContentTicketPayload, total=False):
    tid: str
    tnm: str
    tcl: str


class JwtContentTicketPresenter(ContentTicketPresenter):

    def __init__(self, algorithm: str, private_key: str):
        self._private_key = private_key
        self._algorithm = algorithm

    def present(self, response: CreateContentTicketResponse) -> str:
        payload: ContentTicketPayload = {
            "jti": response["ticket_id"],
            "usr": response["username"],
            "sub": response["user_id"],
            "ref": response["content_ref"],
            "grp": response["project_id"],
            "perms": [permission.value for permission in response["permissions"]],
            "iat": response["issued_at"].timestamp(),
            "exp": response["expire_at"].timestamp(),
        }
        if "team_id" in response:
            payload["tid"] = response["team_id"]
            payload["tnm"] = response["team_name"]
            payload["tcl"] = response["team_color"]
        return jwt.encode(
            payload=payload, key=self._private_key, algorithm=self._algorithm
        )
