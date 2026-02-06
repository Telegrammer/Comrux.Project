__all__ = ["create_remove_member_router"]

from typing import Annotated
from pydantic import UUID4
from starlette import status
from fastapi import APIRouter, Depends, Path
from fastapi.security import HTTPAuthorizationCredentials
from fastapi_error_map import ErrorAwareRouter
from dishka.integrations.fastapi import FromDishka, inject

from domain.exceptions import DomainFieldError, ProjectMustHaveOwnerError
from application.exceptions import (
    CurrentUserNotFoundError,
    ExpiredAccessKeyError,
    ProjectNotFoundError,
    UserNotFoundError,
    AccessDeniedError,
)
from application.ports.mappers.errors import MappingError
from application.ports.gateways.errors import GatewayFailedError
from presentation.models import ProjectMemberRemove, ProjectMemberRemoved
from presentation.handlers import RemoveProjectMemberHandler
from presentation.http.controllers.dependencies import (
    service_unavailable_rule,
    http_bearer,
    log_info,
)


def create_remove_member_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.patch(
        "/{project_id}/remove_member",
        error_map={
            MappingError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            DomainFieldError: status.HTTP_400_BAD_REQUEST,
            ProjectNotFoundError: status.HTTP_404_NOT_FOUND,
            ProjectMustHaveOwnerError: status.HTTP_409_CONFLICT,
            UserNotFoundError: status.HTTP_404_NOT_FOUND,
            CurrentUserNotFoundError: status.HTTP_401_UNAUTHORIZED,
            ExpiredAccessKeyError: status.HTTP_401_UNAUTHORIZED,
            AccessDeniedError: status.HTTP_403_FORBIDDEN,
            GatewayFailedError: service_unavailable_rule,
        },
        default_on_error=log_info,
        status_code=status.HTTP_200_OK,
        response_model=ProjectMemberRemoved,
    )
    @inject
    async def Remove_member(
        project_id: Annotated[UUID4, Path()],
        request_body: ProjectMemberRemove,
        handler: FromDishka[RemoveProjectMemberHandler],
        token: HTTPAuthorizationCredentials = Depends(http_bearer),
    ):

        return await handler(project_id, request_body)

    return router
