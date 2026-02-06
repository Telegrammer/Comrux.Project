__all__ = ["create_list_members_router"]

from typing import Annotated
from starlette import status
from fastapi import APIRouter, Query, Path
from fastapi_error_map import ErrorAwareRouter
from dishka.integrations.fastapi import FromDishka, inject

from domain.exceptions import DomainFieldError
from application.ports.mappers.errors import MappingError
from application.ports.gateways.errors import GatewayFailedError
from application.exceptions import ProjectNotFoundError

from presentation.exceptions import IncorrectQueryParameterError
from presentation.handlers import ListProjectMembersHandler
from presentation.models import ProjectMemberRead
from presentation.http.controllers.dependencies import (
    service_unavailable_rule,
    log_info,
)


def create_list_members_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.get(
        "/{project_id}/members",
        error_map={
            MappingError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            DomainFieldError: status.HTTP_400_BAD_REQUEST,
            GatewayFailedError: service_unavailable_rule,
            IncorrectQueryParameterError: status.HTTP_400_BAD_REQUEST,
            ProjectNotFoundError: status.HTTP_404_NOT_FOUND,
        },
        default_on_error=log_info,
        status_code=status.HTTP_206_PARTIAL_CONTENT,
        response_model=list[ProjectMemberRead],
    )
    @inject
    async def list_members(
        project_id: Annotated[str, Path()],
        handler: FromDishka[ListProjectMembersHandler],
        offset: int = 0,
        limit: int = 10,
        orders: Annotated[str, Query()] = "[]",
    ):
        return await handler(project_id, orders, offset, limit)

    return router
