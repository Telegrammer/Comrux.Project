__all__ = ["create_create_project_router"]

from starlette import status
from fastapi import APIRouter
from fastapi_error_map import ErrorAwareRouter
from dishka.integrations.fastapi import FromDishka, inject

from domain.exceptions import DomainFieldError
from application.exceptions import UserAlreadyExistsError, UserNotFoundError
from application.ports.mappers.errors import MappingError
from application.ports.gateways.errors import GatewayFailedError
from presentation.models import UserCreate, UserCreated
from presentation.handlers import CreateUserHandler



def create_create_user_router() -> APIRouter:
    router = ErrorAwareRouter()

    @router.post(
        "/",
        error_map={
            MappingError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            DomainFieldError: status.HTTP_400_BAD_REQUEST,
            UserAlreadyExistsError: status.HTTP_409_CONFLICT,
            UserNotFoundError: status.HTTP_409_CONFLICT,
            GatewayFailedError: status.HTTP_503_SERVICE_UNAVAILABLE,
        },
        status_code=status.HTTP_201_CREATED,
        response_model=UserCreated,
    )
    @inject
    async def create(
        request_body: UserCreate,
        handler: FromDishka[CreateUserHandler],
    ):
        return await handler(request_body)

    return router