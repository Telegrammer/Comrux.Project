from typing import Annotated
from starlette import status
from fastapi import APIRouter, Path, Depends
from fastapi.security import HTTPAuthorizationCredentials
from fastapi_error_map import ErrorAwareRouter
from dishka.integrations.fastapi import FromDishka, inject
from pydantic import UUID4

from domain.exceptions import DomainFieldError
from application.exceptions import UserNotFoundError
from application.ports.mappers.errors import MappingError
from application.ports.gateways.errors import GatewayFailedError
from presentation.models.user import UserRead
from presentation.handlers import GetCurrentUserHandler
from presentation.http.controllers.dependencies import (
    service_unavailable_rule,
    http_bearer,
)


def create_get_profile_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.get(
        "/me",
        error_map={
            MappingError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            DomainFieldError: status.HTTP_400_BAD_REQUEST,
            UserNotFoundError: status.HTTP_404_NOT_FOUND,
            GatewayFailedError: service_unavailable_rule,
        },
        status_code=status.HTTP_200_OK,
        response_model=UserRead,
    )
    @inject
    async def get_current_user_profile(
        handler: FromDishka[GetCurrentUserHandler],
        token: HTTPAuthorizationCredentials = Depends(http_bearer),
    ):
        return await handler()

    return router
