__all__ = [
    "CreateUserComposition",
]


import logging


from application.ports import UnitOfWork
from application.usecases import (
    CreateUserRequest,
    CreateUserUsecase,
    CreateUserResponse,
)

logger = logging.getLogger(__name__)


class CreateUserComposition:

    def __init__(self, usecase: CreateUserUsecase, unit_of_work: UnitOfWork):
        self._usecase: CreateUserUsecase = usecase
        self._unit_of_work: UnitOfWork = unit_of_work

    async def __call__(self, request: CreateUserRequest) -> CreateUserResponse:
        async with self._unit_of_work:
            logger.info("User creation started")
            response: CreateUserResponse = await self._usecase(request)
            logger.info("User %s was created", response["user_id"])
            return response
