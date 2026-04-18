from typing import Annotated
from pydantic import UUID4
from starlette import status
from fastapi import APIRouter, Depends, Path, Query
from fastapi.security import HTTPAuthorizationCredentials
from fastapi_error_map import ErrorAwareRouter
from dishka.integrations.fastapi import FromDishka, inject

from domain.exceptions import DomainFieldError, AccessRuleMismatchError
from application.exceptions import (
    CurrentUserNotFoundError,
    ExpiredAccessKeyError,
    ProjectNotFoundError,
    AccessListAlreadyExistsError,
    AccessDeniedError,
    ProjectGroupNotInProjectError,
)
from application.ports.mappers.errors import MappingError
from application.ports.gateways.errors import GatewayFailedError
from presentation.models import AccessListCreate, AccessListCreated
from presentation.handlers import CreateAccessListHandler
from presentation.http.controllers.dependencies import (
    service_unavailable_rule,
    http_bearer,
    log_info,
)


def create_add_acl_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.post(
        "/{project_id}/acl",
        error_map={
            MappingError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            DomainFieldError: status.HTTP_400_BAD_REQUEST,
            ProjectNotFoundError: status.HTTP_404_NOT_FOUND,
            AccessListAlreadyExistsError: status.HTTP_409_CONFLICT,
            AccessRuleMismatchError: status.HTTP_409_CONFLICT,
            ProjectGroupNotInProjectError: status.HTTP_409_CONFLICT,
            CurrentUserNotFoundError: status.HTTP_401_UNAUTHORIZED,
            ExpiredAccessKeyError: status.HTTP_401_UNAUTHORIZED,
            AccessDeniedError: status.HTTP_403_FORBIDDEN,
            GatewayFailedError: service_unavailable_rule,
        },
        default_on_error=log_info,
        status_code=status.HTTP_201_CREATED,
        response_model=AccessListCreated,
    )
    @inject
    async def create_access_list(
        project_id: Annotated[UUID4, Path()],
        request_body: AccessListCreate,
        handler: FromDishka[CreateAccessListHandler],
        token: HTTPAuthorizationCredentials = Depends(http_bearer),
        offset: int = 0,
        limit: int = 10_000,
        orders: Annotated[str, Query()] = "[]",
        name: str | None = None,
    ):

        return await handler(
            request_body,
            project_id,
            offset=offset,
            limit=limit,
            orders=orders,
            name=name,
        )

    return router
