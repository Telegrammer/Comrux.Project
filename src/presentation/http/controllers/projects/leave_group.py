__all__ = ["create_leave_group_router"]

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
    ProjectGroupNotFoundError,
    ProjectGroupNotInProjectError,
    ProjectNotFoundError,
)
from application.ports.gateways.errors import GatewayFailedError
from application.ports.mappers.errors import MappingError
from domain.exceptions import DomainFieldError
from presentation.handlers import LeaveProjectGroupHandler
from presentation.http.controllers.dependencies import (
    http_bearer,
    log_info,
    service_unavailable_rule,
)


def create_leave_group_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.delete(
        "/{project_id}/groups/{group_id}/participants/{participant_id}",
        error_map={
            MappingError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            DomainFieldError: status.HTTP_400_BAD_REQUEST,
            ProjectNotFoundError: status.HTTP_404_NOT_FOUND,
            ProjectGroupNotFoundError: status.HTTP_404_NOT_FOUND,
            ProjectGroupNotInProjectError: status.HTTP_404_NOT_FOUND,
            CurrentUserNotFoundError: status.HTTP_401_UNAUTHORIZED,
            ExpiredAccessKeyError: status.HTTP_401_UNAUTHORIZED,
            AccessDeniedError: status.HTTP_403_FORBIDDEN,
            GatewayFailedError: service_unavailable_rule,
        },
        default_on_error=log_info,
        status_code=status.HTTP_204_NO_CONTENT,
    )
    @inject
    async def leave_group(
        project_id: Annotated[UUID4, Path()],
        group_id: Annotated[UUID4, Path()],
        participant_id: Annotated[UUID4, Path()],
        handler: FromDishka[LeaveProjectGroupHandler],
        token: HTTPAuthorizationCredentials = Depends(http_bearer),
    ):
        del token
        await handler(project_id, group_id, participant_id)

    return router
