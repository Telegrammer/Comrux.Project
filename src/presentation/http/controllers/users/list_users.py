from typing import Annotated
from starlette import status
from fastapi import APIRouter, Query
from fastapi_error_map import ErrorAwareRouter
from dishka.integrations.fastapi import FromDishka, inject

from domain.exceptions import DomainFieldError
from application.ports.mappers.errors import MappingError
from application.ports.gateways.errors import GatewayFailedError

from presentation.exceptions import IncorrectQueryParameterError
from presentation.handlers import ListUsersHandler
from presentation.models.user import UserSearchRead
from presentation.http.controllers.dependencies import (
    service_unavailable_rule,
    log_info,
)


def create_list_users_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.get(
        "/",
        error_map={
            MappingError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            DomainFieldError: status.HTTP_400_BAD_REQUEST,
            GatewayFailedError: service_unavailable_rule,
            IncorrectQueryParameterError: status.HTTP_400_BAD_REQUEST,
        },
        default_on_error=log_info,
        status_code=status.HTTP_206_PARTIAL_CONTENT,
        response_model=list[UserSearchRead],
    )
    @inject
    async def list_all(
        handler: FromDishka[ListUsersHandler],
        offset: int = 0,
        limit: int = 10,
        q: Annotated[str, Query()] = "",
        orders: Annotated[str, Query()] = "[]",
    ):
        return await handler(q, orders, offset, limit)

    return router
