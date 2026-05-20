from typing import Annotated
from pydantic import UUID4
from starlette import status
from fastapi import APIRouter, Depends, Path, Query
from fastapi.security import HTTPAuthorizationCredentials
from fastapi_error_map import ErrorAwareRouter
from dishka.integrations.fastapi import FromDishka, inject

from domain.exceptions import DomainFieldError
from application.exceptions import (
    CurrentUserNotFoundError,
    ExpiredAccessKeyError,
    ProjectNotFoundError,
    DocumentNotFoundError,
    DocumentNotInProjectError,
    AccessDeniedError,
    ProjectGroupNotInProjectError,
    UserNotInProjectGroupError,
)
from application.ports.mappers.errors import MappingError
from application.ports.gateways.errors import GatewayFailedError
from presentation.models import ContentTicketCreated
from presentation.handlers import CreateContentTicketHandler
from presentation.http.controllers.dependencies import (
    service_unavailable_rule,
    http_bearer,
    log_info,
)


def create_content_ticket_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.post(
        "/{project_id}/doc/{document_id}/content/ticket",
        error_map={
            MappingError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            DomainFieldError: status.HTTP_400_BAD_REQUEST,
            ProjectNotFoundError: status.HTTP_404_NOT_FOUND,
            DocumentNotFoundError: status.HTTP_404_NOT_FOUND,
            DocumentNotInProjectError: status.HTTP_400_BAD_REQUEST,
            CurrentUserNotFoundError: status.HTTP_401_UNAUTHORIZED,
            ExpiredAccessKeyError: status.HTTP_401_UNAUTHORIZED,
            AccessDeniedError: status.HTTP_403_FORBIDDEN,
            ProjectGroupNotInProjectError: status.HTTP_409_CONFLICT,
            UserNotInProjectGroupError: status.HTTP_409_CONFLICT,
            GatewayFailedError: service_unavailable_rule,
        },
        default_on_error=log_info,
        status_code=status.HTTP_201_CREATED,
        response_model=ContentTicketCreated,
    )
    @inject
    async def access_content_redaction(
        project_id: Annotated[UUID4, Path()],
        document_id: Annotated[UUID4, Path()],
        handler: FromDishka[CreateContentTicketHandler],
        token: HTTPAuthorizationCredentials = Depends(http_bearer),
        team_id: Annotated[UUID4 | None, Query()] = None,
    ):

        return await handler(project_id, document_id, team_id)

    return router
