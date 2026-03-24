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
    DocumentNotInProjectError,
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


def create_assign_document_acl_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.patch(
        "/{project_id}/docs/{document_id}/acl",
        error_map={
            DomainFieldError: status.HTTP_400_BAD_REQUEST,
            ProjectNotFoundError: status.HTTP_404_NOT_FOUND,
            ExpiredAccessKeyError: status.HTTP_401_UNAUTHORIZED,
            CurrentUserNotFoundError: status.HTTP_401_UNAUTHORIZED,
            AccessDeniedError: status.HTTP_403_FORBIDDEN,
            DocumentNotInProjectError: status.HTTP_400_BAD_REQUEST,
            AccessListNotInProjectError: status.HTTP_403_FORBIDDEN,
            GatewayFailedError: service_unavailable_rule,
        },
        default_on_error=log_info,
        status_code=status.HTTP_204_NO_CONTENT,
    )
    @inject
    async def assign_document_acl(
        project_id: Annotated[UUID4, Path()],
        document_id: Annotated[UUID4, Path()],
        request_body: AccessListAssign,
        handler: FromDishka[AssignAccessListHandler],
        token: HTTPAuthorizationCredentials = Depends(http_bearer),
    ) -> None:
        await handler.assign_to_document(
            project_id=project_id,
            document_id=document_id,
            access_list_id=request_body.access_list_id,
        )

    return router

