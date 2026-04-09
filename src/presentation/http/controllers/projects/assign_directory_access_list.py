from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, Path
from fastapi.security import HTTPAuthorizationCredentials
from fastapi_error_map import ErrorAwareRouter
from pydantic import UUID4
from starlette import status

from application.exceptions import (
    AccessDeniedError,
    AccessListNotInProjectError,
    CurrentUserNotFoundError,
    DirectoryNotInProjectError,
    ExpiredAccessKeyError,
    ProjectNotFoundError,
)
from application.ports.gateways.errors import GatewayFailedError
from domain.exceptions import DomainFieldError
from presentation.handlers import AssignAccessListHandler
from presentation.http.controllers.dependencies import (
    http_bearer,
    log_info,
    service_unavailable_rule,
)
from presentation.models import AccessListAssign


def create_assign_directory_acl_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.patch(
        "/{project_id}/dir/{directory_id}/acl",
        error_map={
            DomainFieldError: status.HTTP_400_BAD_REQUEST,
            ExpiredAccessKeyError: status.HTTP_401_UNAUTHORIZED,
            CurrentUserNotFoundError: status.HTTP_401_UNAUTHORIZED,
            AccessDeniedError: status.HTTP_403_FORBIDDEN,
            DirectoryNotInProjectError: status.HTTP_403_FORBIDDEN,
            AccessListNotInProjectError: status.HTTP_403_FORBIDDEN,
            GatewayFailedError: service_unavailable_rule,
        },
        default_on_error=log_info,
        status_code=status.HTTP_204_NO_CONTENT,
    )
    @inject
    async def assign_directory_acl(
        project_id: Annotated[UUID4, Path()],
        directory_id: Annotated[UUID4, Path()],
        request_body: AccessListAssign,
        handler: FromDishka[AssignAccessListHandler],
        token: HTTPAuthorizationCredentials = Depends(http_bearer),
    ) -> None:
        await handler.assign_to_directory(
            project_id=project_id,
            directory_id=directory_id,
            access_list_id=request_body.access_list_id,
        )

    return router
