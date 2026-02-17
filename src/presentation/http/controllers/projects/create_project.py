__all__ = ["create_create_project_router"]

from starlette import status
from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from fastapi_error_map import ErrorAwareRouter
from dishka.integrations.fastapi import FromDishka, inject

from domain.exceptions import DomainFieldError
from application.exceptions import (
    ProjectAlreadyExistsError,
    CurrentUserNotFoundError,
    ExpiredAccessKeyError,
)
from application.ports.mappers.errors import MappingError
from application.ports.gateways.errors import GatewayFailedError
from presentation.models import ProjectCreate, ProjectCreated
from presentation.handlers import CreateProjectHandler
from presentation.http.controllers.dependencies import (
    service_unavailable_rule,
    http_bearer,
    log_info,
)
from presentation.exceptions import InvalidTokenTypeError


def create_create_project_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.post(
        "/",
        error_map={
            MappingError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            DomainFieldError: status.HTTP_400_BAD_REQUEST,
            ProjectAlreadyExistsError: status.HTTP_409_CONFLICT,
            CurrentUserNotFoundError: status.HTTP_401_UNAUTHORIZED,
            ExpiredAccessKeyError: status.HTTP_401_UNAUTHORIZED,
            InvalidTokenTypeError: status.HTTP_401_UNAUTHORIZED,
            GatewayFailedError: service_unavailable_rule,
        },
        default_on_error=log_info,
        status_code=status.HTTP_201_CREATED,
        response_model=ProjectCreated,
    )
    @inject
    async def create(
        request_body: ProjectCreate,
        handler: FromDishka[CreateProjectHandler],
        token: HTTPAuthorizationCredentials = Depends(http_bearer),
    ):
        return await handler(request_body)

    return router
