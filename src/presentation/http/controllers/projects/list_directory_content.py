__all__ = ["create_list_members_router"]

from typing import Annotated
from starlette import status
from pydantic import UUID4
from fastapi import APIRouter, Query, Path
from fastapi_error_map import ErrorAwareRouter
from dishka.integrations.fastapi import FromDishka, inject

from domain.exceptions import DomainFieldError
from application.ports.mappers.errors import MappingError
from application.ports.gateways.errors import GatewayFailedError
from application.exceptions import (
    DirectoryNotFoundError,
    AccessDeniedError,
    DirectoryNotInProjectError,
)

from presentation.exceptions import IncorrectQueryParameterError
from presentation.handlers import ListDirectoryContentHandler
from presentation.models import DocumentRead, DirectoryRead
from presentation.http.controllers.dependencies import (
    service_unavailable_rule,
    log_info,
)


def create_list_directory_content_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.get(
        "/{project_id}/dirs/{directory_id}/content",
        error_map={
            MappingError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            DomainFieldError: status.HTTP_400_BAD_REQUEST,
            GatewayFailedError: service_unavailable_rule,
            IncorrectQueryParameterError: status.HTTP_400_BAD_REQUEST,
            AccessDeniedError: status.HTTP_403_FORBIDDEN,
            DirectoryNotInProjectError: status.HTTP_400_BAD_REQUEST,
            DirectoryNotFoundError: status.HTTP_404_NOT_FOUND,
        },
        default_on_error=log_info,
        status_code=status.HTTP_206_PARTIAL_CONTENT,
        response_model=list[DocumentRead | DirectoryRead],
    )
    @inject
    async def list_directory_content(
        project_id: Annotated[UUID4, Path()],
        directory_id: Annotated[UUID4, Path()],
        handler: FromDishka[ListDirectoryContentHandler],
        offset: int = 0,
        limit: int = 10,
        orders: Annotated[str, Query()] = "[]",
    ):
        return await handler(project_id, directory_id, offset, limit, orders)

    return router
