__all__ = ["create_list_projects_router"]

from typing import Annotated
from starlette import status
from fastapi import APIRouter, Query
from fastapi_error_map import ErrorAwareRouter
from dishka.integrations.fastapi import FromDishka, inject

from domain.exceptions import DomainFieldError
from application.ports.mappers.errors import MappingError
from application.ports.gateways.errors import GatewayFailedError

from presentation.exceptions import IncorrectQueryParameterError
from presentation.handlers import ListProjectsHandler
from presentation.models import ProjectRead

def create_list_projects_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.get(
        "/list",
        error_map={
            MappingError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            DomainFieldError: status.HTTP_400_BAD_REQUEST,
            GatewayFailedError: status.HTTP_503_SERVICE_UNAVAILABLE,
            IncorrectQueryParameterError: status.HTTP_400_BAD_REQUEST,
        },
        status_code=status.HTTP_206_PARTIAL_CONTENT,
        response_model=list[ProjectRead],
    )
    @inject
    async def list_all(
        handler: FromDishka[ListProjectsHandler],
        offset: int = 0,
        limit: int = 10,
        orders: Annotated[str, Query()] = "[]",
    ):
        return await handler(orders, offset, limit)

    return router