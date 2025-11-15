__all__ = ["create_create_project_router"]

from starlette import status
from fastapi import APIRouter
from fastapi_error_map import ErrorAwareRouter
from dishka.integrations.fastapi import FromDishka, inject

from domain.exceptions import DomainFieldError
from application.exceptions import ProjectAlreadyExistsError
from application.ports.mappers.errors import MappingError
from application.ports.gateways.errors import GatewayFailedError
from presentation.models import ProjectCreate, ProjectCreated
from presentation.handlers import CreateProjectHandler



def create_create_project_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.post(
        "/create",
        error_map={
            MappingError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            DomainFieldError: status.HTTP_400_BAD_REQUEST,
            ProjectAlreadyExistsError: status.HTTP_409_CONFLICT,
            GatewayFailedError: status.HTTP_503_SERVICE_UNAVAILABLE,
        },
        status_code=status.HTTP_201_CREATED,
        response_model=ProjectCreated,
    )
    @inject
    async def create(
        request_body: ProjectCreate,
        handler: FromDishka[CreateProjectHandler],
    ):
        return await handler(request_body)

    return router