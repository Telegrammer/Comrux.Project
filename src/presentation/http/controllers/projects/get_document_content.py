from typing import Annotated

from fastapi import APIRouter, Depends, Path, Response
from fastapi.security import HTTPAuthorizationCredentials
from fastapi_error_map import ErrorAwareRouter
from pydantic import UUID4
from starlette import status
from dishka.integrations.fastapi import FromDishka, inject

from domain.exceptions import DomainFieldError
from application.exceptions import (
    AccessDeniedError,
    CurrentUserNotFoundError,
    DocumentNotFoundError,
    DocumentNotInProjectError,
    ExpiredAccessKeyError,
    ProjectNotFoundError,
)
from application.ports.gateways.errors import GatewayFailedError
from application.ports.mappers.errors import MappingError
from presentation.handlers import GetDocumentContentHandler
from presentation.http.controllers.dependencies import (
    log_info,
    optional_bearer,
    service_unavailable_rule,
)


def create_get_document_content_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.get(
        "/{project_id}/doc/{document_id}/content",
        error_map={
            MappingError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            DomainFieldError: status.HTTP_400_BAD_REQUEST,
            ProjectNotFoundError: status.HTTP_404_NOT_FOUND,
            DocumentNotFoundError: status.HTTP_404_NOT_FOUND,
            DocumentNotInProjectError: status.HTTP_400_BAD_REQUEST,
            CurrentUserNotFoundError: status.HTTP_401_UNAUTHORIZED,
            ExpiredAccessKeyError: status.HTTP_401_UNAUTHORIZED,
            AccessDeniedError: status.HTTP_403_FORBIDDEN,
            GatewayFailedError: service_unavailable_rule,
        },
        default_on_error=log_info,
        status_code=status.HTTP_200_OK,
        response_class=Response,
        responses={200: {"content": {"application/octet-stream": {}}}},
    )
    @inject
    async def get_document_content(
        project_id: Annotated[UUID4, Path()],
        document_id: Annotated[UUID4, Path()],
        handler: FromDishka[GetDocumentContentHandler],
        token: Annotated[
            HTTPAuthorizationCredentials | None, Depends(optional_bearer)
        ],
    ) -> Response:
        del token
        content: bytes = await handler(project_id, document_id)
        return Response(content=content, media_type="application/octet-stream")

    return router
