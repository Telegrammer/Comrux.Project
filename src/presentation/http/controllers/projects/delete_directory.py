__all__ = ["create_delete_project_router"]

from typing import Annotated
from pydantic import UUID4
from starlette import status
from fastapi import APIRouter, Path, Depends
from fastapi.security import HTTPAuthorizationCredentials
from fastapi_error_map import ErrorAwareRouter
from dishka.integrations.fastapi import FromDishka, inject

from domain.exceptions import DomainFieldError
from application.ports.mappers.errors import MappingError
from application.ports.gateways.errors import GatewayFailedError
from application.exceptions import (
    ExpiredAccessKeyError,
    AccessDeniedError,
    CurrentUserNotFoundError,
    DirectoryNotInProjectError,
    ProjectNotFoundError,
)
from presentation.handlers import DeleteDirectoryHandler
from presentation.http.controllers.dependencies import (
    http_bearer,
    service_unavailable_rule,
    log_info,
)


def create_delete_directory_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.delete(
        "/{project_id}/dirs/{directory_id}/",
        error_map={
            DomainFieldError: status.HTTP_400_BAD_REQUEST,
            ProjectNotFoundError: status.HTTP_404_NOT_FOUND,
            ExpiredAccessKeyError: status.HTTP_401_UNAUTHORIZED,
            CurrentUserNotFoundError: status.HTTP_401_UNAUTHORIZED,
            AccessDeniedError: status.HTTP_403_FORBIDDEN,
            DirectoryNotInProjectError: status.HTTP_403_FORBIDDEN,
            GatewayFailedError: service_unavailable_rule,
        },
        default_on_error=log_info,
        status_code=status.HTTP_204_NO_CONTENT,
    )
    @inject
    async def delete_directory(
        project_id: Annotated[UUID4, Path()],
        directory_id: Annotated[UUID4, Path()],
        handler: FromDishka[DeleteDirectoryHandler],
        token: HTTPAuthorizationCredentials = Depends(http_bearer),
    ):
        return await handler(project_id, directory_id)

    return router
