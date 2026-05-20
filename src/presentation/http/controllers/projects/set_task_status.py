__all__ = ["create_set_task_status_router"]

from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, Path
from fastapi.security import HTTPAuthorizationCredentials
from fastapi_error_map import ErrorAwareRouter
from pydantic import UUID4
from starlette import status

from application.exceptions import (
    AccessDeniedError,
    CurrentUserNotFoundError,
    ExpiredAccessKeyError,
    ProjectTaskNotFoundError,
)
from application.ports.gateways.errors import GatewayFailedError
from application.ports.mappers.errors import MappingError
from domain.exceptions import (
    DomainError,
    DomainFieldError,
    ProjectTaskInvalidStatusTransitionError,
)
from presentation.handlers import SetProjectTaskStatusHandler
from presentation.http.controllers.dependencies import (
    http_bearer,
    log_info,
    service_unavailable_rule,
)
from presentation.models import ProjectTaskSetStatus, ProjectTaskStatusChanged


def create_set_task_status_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.patch(
        "/tasks/{task_id}/status",
        error_map={
            MappingError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            DomainFieldError: status.HTTP_400_BAD_REQUEST,
            ProjectTaskInvalidStatusTransitionError: status.HTTP_409_CONFLICT,
            DomainError: status.HTTP_409_CONFLICT,
            ProjectTaskNotFoundError: status.HTTP_404_NOT_FOUND,
            CurrentUserNotFoundError: status.HTTP_401_UNAUTHORIZED,
            ExpiredAccessKeyError: status.HTTP_401_UNAUTHORIZED,
            AccessDeniedError: status.HTTP_403_FORBIDDEN,
            GatewayFailedError: service_unavailable_rule,
        },
        default_on_error=log_info,
        status_code=status.HTTP_200_OK,
        response_model=ProjectTaskStatusChanged,
    )
    @inject
    async def set_task_status(
        task_id: Annotated[UUID4, Path()],
        request_body: ProjectTaskSetStatus,
        handler: FromDishka[SetProjectTaskStatusHandler],
        token: HTTPAuthorizationCredentials = Depends(http_bearer),
    ):
        del token
        return await handler(task_id, request_body)

    return router
