__all__ = ["create_join_group_router"]

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
    ProjectGroupParticipantNotInProjectError,
    ProjectNotFoundError,
    UserNotFoundError,
)
from application.ports.gateways.errors import GatewayFailedError
from application.ports.mappers.errors import MappingError
from domain.exceptions import DomainFieldError, ProjectGroupAdmissionError
from presentation.handlers import JoinProjectGroupHandler
from presentation.http.controllers.dependencies import (
    http_bearer,
    log_info,
    service_unavailable_rule,
)
from presentation.models import ProjectGroupJoin


def create_join_group_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.put(
        "/{project_id}/groups/{group_id}/participants",
        error_map={
            MappingError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            DomainFieldError: status.HTTP_400_BAD_REQUEST,
            ProjectNotFoundError: status.HTTP_404_NOT_FOUND,
            ProjectGroupNotFoundError: status.HTTP_404_NOT_FOUND,
            ProjectGroupNotInProjectError: status.HTTP_404_NOT_FOUND,
            UserNotFoundError: status.HTTP_404_NOT_FOUND,
            ProjectGroupParticipantNotInProjectError: status.HTTP_409_CONFLICT,
            ProjectGroupAdmissionError: status.HTTP_409_CONFLICT,
            CurrentUserNotFoundError: status.HTTP_401_UNAUTHORIZED,
            ExpiredAccessKeyError: status.HTTP_401_UNAUTHORIZED,
            AccessDeniedError: status.HTTP_403_FORBIDDEN,
            GatewayFailedError: service_unavailable_rule,
        },
        default_on_error=log_info,
        status_code=status.HTTP_204_NO_CONTENT,
    )
    @inject
    async def join_group(
        project_id: Annotated[UUID4, Path()],
        group_id: Annotated[UUID4, Path()],
        request_body: ProjectGroupJoin,
        handler: FromDishka[JoinProjectGroupHandler],
        token: HTTPAuthorizationCredentials = Depends(http_bearer),
    ):
        del token
        await handler(project_id, group_id, request_body)

    return router
