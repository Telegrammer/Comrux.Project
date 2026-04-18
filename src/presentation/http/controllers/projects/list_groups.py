__all__ = ["create_list_groups_router"]

from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Path, Query
from fastapi_error_map import ErrorAwareRouter
from pydantic import UUID4
from starlette import status

from application.exceptions import (
    AccessDeniedError,
    CurrentUserNotFoundError,
    ExpiredAccessKeyError,
    ProjectNotFoundError,
)
from application.ports.gateways.errors import GatewayFailedError
from application.ports.mappers.errors import MappingError
from domain.exceptions import DomainFieldError
from presentation.handlers import ListProjectGroupsHandler
from presentation.http.controllers.dependencies import (
    log_info,
    service_unavailable_rule,
)
from presentation.models import ProjectGroupRead


def create_list_groups_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.get(
        "/{project_id}/groups",
        error_map={
            MappingError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            DomainFieldError: status.HTTP_400_BAD_REQUEST,
            ProjectNotFoundError: status.HTTP_404_NOT_FOUND,
            CurrentUserNotFoundError: status.HTTP_401_UNAUTHORIZED,
            ExpiredAccessKeyError: status.HTTP_401_UNAUTHORIZED,
            AccessDeniedError: status.HTTP_403_FORBIDDEN,
            GatewayFailedError: service_unavailable_rule,
        },
        default_on_error=log_info,
        status_code=status.HTTP_206_PARTIAL_CONTENT,
        response_model=list[ProjectGroupRead],
    )
    @inject
    async def list_groups(
        project_id: Annotated[UUID4, Path()],
        handler: FromDishka[ListProjectGroupsHandler],
        offset: int = 0,
        limit: int = 10,
        orders: Annotated[str, Query()] = "[]",
        name: str | None = None,
    ):
        return await handler(project_id, orders, offset, limit, name)

    return router
