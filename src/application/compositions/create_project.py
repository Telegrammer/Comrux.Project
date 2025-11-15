__all__ = [
    "CreateProjectComposition",
]


import logging


from application.ports import UnitOfWork
from application.usecases import (
    CreateProjectRequest,
    CreateProjectUsecase,
    CreateProjectResponse,
)

logger = logging.getLogger(__name__)


class CreateProjectComposition:

    def __init__(self, usecase: CreateProjectUsecase, unit_of_work: UnitOfWork):
        self._usecase: CreateProjectUsecase = usecase
        self._unit_of_work: UnitOfWork = unit_of_work

    async def __call__(self, request: CreateProjectRequest) -> CreateProjectResponse:
        async with self._unit_of_work:
            logger.info("Project creation started")
            response = await self._usecase(request)
            logger.info("Project created")
            return response
