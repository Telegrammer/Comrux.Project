__all__ = ["create_get_task_router"]

from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Path
from fastapi_error_map import ErrorAwareRouter
from pydantic import UUID4
from starlette import status

from application.exceptions import (
    AccessDeniedError,
    CurrentUserNotFoundError,
    ExpiredAccessKeyError,
    ProjectNotFoundError,
    ProjectTaskNotFoundError,
    ProjectTaskNotInProjectError,
)
from application.ports.gateways.errors import GatewayFailedError
from application.ports.mappers.errors import MappingError
from domain.exceptions import DomainError, DomainFieldError
from presentation.handlers import GetProjectTaskHandler
from presentation.http.controllers.dependencies import (
    log_info,
    service_unavailable_rule,
)
from presentation.models import ProjectTaskDetailsRead


def create_get_task_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.get(
        "/{project_id}/tasks/{task_id}",
        error_map={
            MappingError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            DomainFieldError: status.HTTP_400_BAD_REQUEST,
            DomainError: status.HTTP_409_CONFLICT,
            ProjectNotFoundError: status.HTTP_404_NOT_FOUND,
            ProjectTaskNotFoundError: status.HTTP_404_NOT_FOUND,
            ProjectTaskNotInProjectError: status.HTTP_404_NOT_FOUND,
            CurrentUserNotFoundError: status.HTTP_401_UNAUTHORIZED,
            ExpiredAccessKeyError: status.HTTP_401_UNAUTHORIZED,
            AccessDeniedError: status.HTTP_403_FORBIDDEN,
            GatewayFailedError: service_unavailable_rule,
        },
        default_on_error=log_info,
        status_code=status.HTTP_200_OK,
        response_model=ProjectTaskDetailsRead,
    )
    @inject
    async def get_task(
        project_id: Annotated[UUID4, Path()],
        task_id: Annotated[UUID4, Path()],
        handler: FromDishka[GetProjectTaskHandler],
    ):
        return await handler(project_id, task_id)

    return router
