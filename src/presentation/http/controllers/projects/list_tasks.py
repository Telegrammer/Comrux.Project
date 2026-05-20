__all__ = ["create_list_tasks_router"]

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
from domain.exceptions import DomainError, DomainFieldError
from presentation.handlers import ListProjectTasksHandler
from presentation.http.controllers.dependencies import (
    log_info,
    service_unavailable_rule,
)
from presentation.models import ProjectTaskRead


def create_list_tasks_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.get(
        "/{project_id}/tasks",
        error_map={
            MappingError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            DomainFieldError: status.HTTP_400_BAD_REQUEST,
            DomainError: status.HTTP_409_CONFLICT,
            ProjectNotFoundError: status.HTTP_404_NOT_FOUND,
            CurrentUserNotFoundError: status.HTTP_401_UNAUTHORIZED,
            ExpiredAccessKeyError: status.HTTP_401_UNAUTHORIZED,
            AccessDeniedError: status.HTTP_403_FORBIDDEN,
            GatewayFailedError: service_unavailable_rule,
        },
        default_on_error=log_info,
        status_code=status.HTTP_206_PARTIAL_CONTENT,
        response_model=list[ProjectTaskRead],
    )
    @inject
    async def list_tasks(
        project_id: Annotated[UUID4, Path()],
        handler: FromDishka[ListProjectTasksHandler],
        offset: int = 0,
        limit: int = 10,
        orders: Annotated[str, Query()] = "[]",
        name: str | None = Query(default=None, alias="name"),
        status_filter: str | None = Query(default=None, alias="status"),
        scope: str | None = Query(default=None, alias="filter"),
    ):
        return await handler(project_id, orders, offset, limit, name, status_filter, scope)

    return router
