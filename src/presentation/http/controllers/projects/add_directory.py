__all__ = ["create_add_member_router"]

from typing import Annotated
from pydantic import UUID4
from starlette import status
from fastapi import APIRouter, Depends, Path
from fastapi.security import HTTPAuthorizationCredentials
from fastapi_error_map import ErrorAwareRouter
from dishka.integrations.fastapi import FromDishka, inject

from domain.exceptions import DomainFieldError
from application.exceptions import (
    CurrentUserNotFoundError,
    ExpiredAccessKeyError,
    ProjectNotFoundError,
    DirectoryNotFoundError,
    DirectoryAlreadyExistsError,
    AccessDeniedError,
)
from application.ports.mappers.errors import MappingError
from application.ports.gateways.errors import GatewayFailedError
from presentation.models import DirectoryCreate, DirectoryCreated
from presentation.handlers import CreateDirectoryHandler
from presentation.http.controllers.dependencies import (
    service_unavailable_rule,
    http_bearer,
    log_info,
)


def create_add_directory_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.post(
        "/{project_id}/dirs",
        error_map={
            MappingError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            DomainFieldError: status.HTTP_400_BAD_REQUEST,
            ProjectNotFoundError: status.HTTP_404_NOT_FOUND,
            DirectoryNotFoundError: status.HTTP_404_NOT_FOUND,
            DirectoryAlreadyExistsError: status.HTTP_409_CONFLICT,
            CurrentUserNotFoundError: status.HTTP_401_UNAUTHORIZED,
            ExpiredAccessKeyError: status.HTTP_401_UNAUTHORIZED,
            AccessDeniedError: status.HTTP_403_FORBIDDEN,
            GatewayFailedError: service_unavailable_rule,
        },
        default_on_error=log_info,
        status_code=status.HTTP_201_CREATED,
        response_model=DirectoryCreated,
    )
    @inject
    async def create_directory(
        project_id: Annotated[UUID4, Path()],
        request_body: DirectoryCreate,
        handler: FromDishka[CreateDirectoryHandler],
        token: HTTPAuthorizationCredentials = Depends(http_bearer),
    ):

        return await handler(project_id, request_body)

    return router
