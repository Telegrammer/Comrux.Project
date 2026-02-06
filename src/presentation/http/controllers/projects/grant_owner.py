__all__ = ["create_add_member_router"]

from typing import Annotated
from pydantic import UUID4
from starlette import status
from fastapi import APIRouter, Depends, Path
from fastapi.security import HTTPAuthorizationCredentials
from fastapi_error_map import ErrorAwareRouter
from dishka.integrations.fastapi import FromDishka, inject

from domain.exceptions import DomainFieldError, MemberNotFoundError
from application.exceptions import (
    CurrentUserNotFoundError,
    ExpiredAccessKeyError,
    ProjectNotFoundError,
    UserNotFoundError,
    AccessDeniedError,
)
from application.ports.mappers.errors import MappingError
from application.ports.gateways.errors import GatewayFailedError
from presentation.models import ProjectGrantOwner, ProjectOwnerGranted
from presentation.handlers import GrantOwnerHandler
from presentation.http.controllers.dependencies import (
    service_unavailable_rule,
    http_bearer,
    log_info,
)


def create_grant_owner_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.put(
        "/{project_id}/owner",
        error_map={
            MappingError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            DomainFieldError: status.HTTP_400_BAD_REQUEST,
            MemberNotFoundError: status.HTTP_404_NOT_FOUND,
            ProjectNotFoundError: status.HTTP_404_NOT_FOUND,
            UserNotFoundError: status.HTTP_404_NOT_FOUND,
            CurrentUserNotFoundError: status.HTTP_401_UNAUTHORIZED,
            ExpiredAccessKeyError: status.HTTP_401_UNAUTHORIZED,
            AccessDeniedError: status.HTTP_403_FORBIDDEN,
            GatewayFailedError: service_unavailable_rule,
        },
        default_on_error=log_info,
        status_code=status.HTTP_200_OK,
        response_model=ProjectOwnerGranted,
    )
    @inject
    async def transfer_ownership(
        project_id: Annotated[UUID4, Path()],
        request_body: ProjectGrantOwner,
        handler: FromDishka[GrantOwnerHandler],
        token: HTTPAuthorizationCredentials = Depends(http_bearer),
    ):

        return await handler(project_id, request_body)

    return router
