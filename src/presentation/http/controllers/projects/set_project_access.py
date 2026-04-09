from typing import Annotated
from starlette import status
from fastapi import APIRouter, Path, Depends, Body
from fastapi.security import HTTPAuthorizationCredentials
from fastapi_error_map import ErrorAwareRouter
from dishka.integrations.fastapi import FromDishka, inject

from domain.exceptions import DomainFieldError
from application.exceptions import (
    ExpiredAccessKeyError,
    CurrentUserNotFoundError,
    AccessDeniedError,
    ProjectNotFoundError,
)
from application.ports.mappers.errors import MappingError
from application.ports.gateways.errors import GatewayFailedError
from presentation.models import ProjectSetAccess
from presentation.handlers import SetProjectAccessHandler
from presentation.http.controllers.dependencies import (
    service_unavailable_rule,
    http_bearer,
    log_info,
)


def create_set_project_access_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.patch(
        "/{project_id}/access",
        error_map={
            MappingError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            DomainFieldError: status.HTTP_400_BAD_REQUEST,
            ProjectNotFoundError: status.HTTP_404_NOT_FOUND,
            ExpiredAccessKeyError: status.HTTP_401_UNAUTHORIZED,
            CurrentUserNotFoundError: status.HTTP_401_UNAUTHORIZED,
            AccessDeniedError: status.HTTP_403_FORBIDDEN,
            GatewayFailedError: service_unavailable_rule,
        },
        default_on_error=log_info,
        status_code=status.HTTP_204_NO_CONTENT,
    )
    @inject
    async def set_access(
        project_id: Annotated[str, Path()],
        request_body: ProjectSetAccess,
        handler: FromDishka[SetProjectAccessHandler],
        token: HTTPAuthorizationCredentials = Depends(http_bearer),
    ):
        return await handler(project_id, request_body.is_private)

    return router
