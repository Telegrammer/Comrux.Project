__all__ = ["create_update_project_router"]

from typing import Annotated
from starlette import status
from fastapi import APIRouter, Path, Depends
from fastapi.security import HTTPAuthorizationCredentials
from fastapi_error_map import ErrorAwareRouter
from dishka.integrations.fastapi import FromDishka, inject

from domain.exceptions import DomainFieldError
from application.exceptions import (
    ExpiredAccessKeyError,
    CurrentUserNotFoundError,
    AccessDeniedError,
)
from application.ports.mappers.errors import MappingError
from application.ports.gateways.errors import GatewayFailedError
from presentation.models import ProjectUpdate
from presentation.handlers import UpdateProjectHandler
from presentation.http.controllers.dependencies import (
    service_unavailable_rule,
    http_bearer,
    log_info,
)


def create_update_project_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.patch(
        "/{project_id}",
        error_map={
            MappingError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            DomainFieldError: status.HTTP_400_BAD_REQUEST,
            ExpiredAccessKeyError: status.HTTP_401_UNAUTHORIZED,
            CurrentUserNotFoundError: status.HTTP_401_UNAUTHORIZED,
            AccessDeniedError: status.HTTP_403_FORBIDDEN,
            GatewayFailedError: service_unavailable_rule,
        },
        default_on_error=log_info,
        status_code=status.HTTP_204_NO_CONTENT,
    )
    @inject
    async def update(
        project_id: Annotated[str, Path()],
        request_body: ProjectUpdate,
        handler: FromDishka[UpdateProjectHandler],
        token: HTTPAuthorizationCredentials = Depends(http_bearer),
    ):
        return await handler(project_id, request_body)

    return router
