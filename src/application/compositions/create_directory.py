import logging


from application.ports import UnitOfWork
from application.usecases import (
    CreateDirectoryRequest,
    CreateDirectoryUsecase,
    CreateDirectoryResponse,
)

logger = logging.getLogger(__name__)


class CreateDirectoryComposition:

    def __init__(self, usecase: CreateDirectoryUsecase, unit_of_work: UnitOfWork):
        self._usecase: CreateDirectoryUsecase = usecase
        self._unit_of_work: UnitOfWork = unit_of_work

    async def __call__(
        self, request: CreateDirectoryRequest
    ) -> CreateDirectoryResponse:
        async with self._unit_of_work:
            logger.info("Directory creation started")
            response: CreateDirectoryResponse = await self._usecase(request)
        logger.info("Directory %s was created", response["directory"])
        return response
