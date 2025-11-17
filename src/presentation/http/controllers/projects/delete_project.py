__all__ = ["create_delete_project_router"]

from typing import Annotated
from starlette import status
from fastapi import APIRouter, Path
from fastapi_error_map import ErrorAwareRouter
from dishka.integrations.fastapi import FromDishka, inject

from domain.exceptions import DomainFieldError
from application.ports.mappers.errors import MappingError
from application.ports.gateways.errors import GatewayFailedError
from presentation.handlers import DeleteProjectHandler



def create_delete_project_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.delete(
        "/{project_id}",
        error_map={
            MappingError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            DomainFieldError: status.HTTP_400_BAD_REQUEST,
            GatewayFailedError: status.HTTP_503_SERVICE_UNAVAILABLE,
        },
        status_code=status.HTTP_204_NO_CONTENT,
    )
    @inject
    async def update(
        project_id: Annotated[str, Path()],
        handler: FromDishka[DeleteProjectHandler],
    ):
        return await handler(project_id)

    return router