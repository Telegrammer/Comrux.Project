import logging

from application.ports import UnitOfWork
from application.usecases import (
    GetProjectTaskRequest,
    GetProjectTaskResponse,
    GetProjectTaskUsecase,
)

logger = logging.getLogger(__name__)


class GetProjectTaskComposition:
    def __init__(self, unit_of_work: UnitOfWork, usecase: GetProjectTaskUsecase):
        self._unit_of_work = unit_of_work
        self._usecase = usecase

    async def __call__(self, request: GetProjectTaskRequest) -> GetProjectTaskResponse:
        async with self._unit_of_work:
            logger.info("Getting task %s", request.task_id.value)
            response = await self._usecase(request)
        logger.info("Fetched task %s", response["id_"])
        return response
