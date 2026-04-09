__all__ = ["InjectCurrentUserIdMiddleware"]


from typing import Awaitable, Callable, Optional, Type

from dishka import DependencyKey
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.types import ASGIApp

from domain import UserId

from presentation.models import AuthInfo

from .update_context import update_context


class InjectCurrentUserIdMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        dispatch: Optional[
            Callable[
                [Request, Callable[[Request], Awaitable[Response]]], Awaitable[Response]
            ]
        ] = None,
    ) -> None:
        super().__init__(app, dispatch=update_context(self.dispatch))

    async def dispatch(self, request: Request) -> dict[DependencyKey, object | Type]:

        auth_info: AuthInfo = getattr(request.state, "auth_info", None)

        if not (auth_info and auth_info.user_id):
            return {UserId | None: None}

        return {UserId | None: UserId(auth_info.user_id)}
