__all__ = ["create_list_group_members_router"]

from typing import Annotated

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Path, Query
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
from presentation.handlers import ListProjectGroupMembersHandler
from presentation.http.controllers.dependencies import (
    log_info,
    service_unavailable_rule,
)
from presentation.models import ProjectMemberRead


def create_list_group_members_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.get(
        "/{project_id}/groups/{group_id}/participants",
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
        status_code=status.HTTP_206_PARTIAL_CONTENT,
        response_model=list[ProjectMemberRead],
    )
    @inject
    async def list_group_members(
        project_id: Annotated[UUID4, Path()],
        group_id: Annotated[UUID4, Path()],
        handler: FromDishka[ListProjectGroupMembersHandler],
        offset: int = 0,
        limit: int = 10,
        orders: Annotated[str, Query()] = "[]",
    ):
        return await handler(project_id, group_id, orders, offset, limit)

    return router
