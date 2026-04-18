__all__ = ["create_create_group_router"]

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
    ProjectGroupAlreadyExistsError,
    ProjectNotFoundError,
)
from application.ports.gateways.errors import GatewayFailedError
from application.ports.mappers.errors import MappingError
from domain.exceptions import DomainFieldError, ProjectGroupOwnerInParticipantsError
from presentation.handlers import CreateProjectGroupHandler
from presentation.http.controllers.dependencies import (
    http_bearer,
    log_info,
    service_unavailable_rule,
)
from presentation.models import ProjectGroupCreate, ProjectGroupCreated


def create_create_group_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.post(
        "/{project_id}/groups",
        error_map={
            MappingError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            DomainFieldError: status.HTTP_400_BAD_REQUEST,
            ProjectGroupOwnerInParticipantsError: status.HTTP_409_CONFLICT,
            ProjectNotFoundError: status.HTTP_404_NOT_FOUND,
            ProjectGroupAlreadyExistsError: status.HTTP_409_CONFLICT,
            CurrentUserNotFoundError: status.HTTP_401_UNAUTHORIZED,
            ExpiredAccessKeyError: status.HTTP_401_UNAUTHORIZED,
            AccessDeniedError: status.HTTP_403_FORBIDDEN,
            GatewayFailedError: service_unavailable_rule,
        },
        default_on_error=log_info,
        status_code=status.HTTP_201_CREATED,
        response_model=ProjectGroupCreated,
    )
    @inject
    async def create_group(
        project_id: Annotated[UUID4, Path()],
        request_body: ProjectGroupCreate,
        handler: FromDishka[CreateProjectGroupHandler],
        token: HTTPAuthorizationCredentials = Depends(http_bearer),
    ):
        del token
        return await handler(project_id, request_body)

    return router
