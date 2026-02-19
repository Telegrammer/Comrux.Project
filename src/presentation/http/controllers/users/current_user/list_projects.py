__all__ = ["create_list_projects_router"]

from typing import Annotated
from starlette import status
from fastapi import APIRouter, Query, Depends
from fastapi.security import HTTPAuthorizationCredentials
from fastapi_error_map import ErrorAwareRouter
from dishka.integrations.fastapi import FromDishka, inject

from domain.exceptions import DomainFieldError
from domain.enums import ProjectRole
from application.exceptions import UserNotFoundError
from application.exceptions.authorization import ExpiredAccessKeyError
from application.ports.mappers.errors import MappingError
from application.ports.gateways.errors import GatewayFailedError

from presentation.exceptions import IncorrectQueryParameterError
from presentation.handlers import ListCurrentUserProjectsHandler
from presentation.models import CurrentUserProjectRead
from presentation.http.controllers.dependencies import (
    service_unavailable_rule,
    log_info,
    http_bearer
)


def create_list_projects_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.get(
        "/projects",
        error_map={
            MappingError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            UserNotFoundError: status.HTTP_401_UNAUTHORIZED,
            DomainFieldError: status.HTTP_400_BAD_REQUEST,
            ExpiredAccessKeyError: status.HTTP_401_UNAUTHORIZED,
            GatewayFailedError: service_unavailable_rule,
            IncorrectQueryParameterError: status.HTTP_400_BAD_REQUEST,
        },
        default_on_error=log_info,
        status_code=status.HTTP_206_PARTIAL_CONTENT,
        response_model=list[CurrentUserProjectRead],
        response_model_exclude_none=True
    )
    @inject
    async def list_my_projects(
        handler: FromDishka[ListCurrentUserProjectsHandler],
        role: Annotated[str, Query()] = "",
        offset: int = 0,
        limit: int = 10,
        orders: Annotated[str, Query()] = "[]",
        token: HTTPAuthorizationCredentials = Depends(http_bearer)
    ):
        return await handler(role, orders, offset, limit)

    return router
