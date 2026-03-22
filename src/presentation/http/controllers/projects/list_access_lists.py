from typing import Annotated
from starlette import status
from pydantic import UUID4
from fastapi import APIRouter, Query, Path
from fastapi_error_map import ErrorAwareRouter
from dishka.integrations.fastapi import FromDishka, inject

from domain.exceptions import DomainFieldError
from application.ports.mappers.errors import MappingError
from application.ports.gateways.errors import GatewayFailedError
from application.exceptions import (
    ProjectNotFoundError,
    AccessDeniedError,
)

from presentation.exceptions import IncorrectQueryParameterError
from presentation.handlers import ListProjectAccessListsHandler
from presentation.models import AccessListRead
from presentation.http.controllers.dependencies import (
    service_unavailable_rule,
    log_info,
)


def create_list_acls_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.get(
        "/{project_id}/acl",
        error_map={
            MappingError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            DomainFieldError: status.HTTP_400_BAD_REQUEST,
            GatewayFailedError: service_unavailable_rule,
            IncorrectQueryParameterError: status.HTTP_400_BAD_REQUEST,
            AccessDeniedError: status.HTTP_403_FORBIDDEN,
            ProjectNotFoundError: status.HTTP_404_NOT_FOUND,
        },
        default_on_error=log_info,
        status_code=status.HTTP_206_PARTIAL_CONTENT,
        response_model=list[AccessListRead],
    )
    @inject
    async def list_access_lists(
        project_id: Annotated[UUID4, Path()],
        handler: FromDishka[ListProjectAccessListsHandler],
        offset: int = 0,
        limit: int = 10,
        name: Annotated[str, Query()] = "",
        orders: Annotated[str, Query()] = "[]",
    ):
        filters: dict[str, str] = {"name": name}
        return await handler(
            project_id=project_id,
            offset=offset,
            limit=limit,
            raw_orders=orders,
            raw_filters=filters,
        )

    return router
