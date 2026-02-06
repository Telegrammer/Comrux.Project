__all__ = ["InjectAuthInfoMiddleware"]


from typing import Awaitable, Callable, Optional, Type

from dishka import AsyncContainer, DependencyKey
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from starlette.types import ASGIApp


from presentation.models import AuthInfo

from .extratctors import AuthInfoExtractor
from .update_context import update_context


class InjectAuthInfoMiddleware(BaseHTTPMiddleware):

    def __init__(
        self,
        app: ASGIApp,
        dispatch: Optional[
            Callable[
                [Request, Callable[[Request], Awaitable[Response]]], Awaitable[Response]
            ]
        ] = None,
    ) -> None:
        self._auth_info_extractor = None
        super().__init__(app, dispatch)

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:

        if not self._auth_info_extractor:
            app_container: AsyncContainer = request.app.state.dishka_container
            self._auth_info_extractor = await app_container.get(AuthInfoExtractor)

        request.state.auth_info = await self._auth_info_extractor(request)

        return await call_next(request)
