import logging

from application.ports import UnitOfWork
from application.ports.gateways.query_params import ProjectTaskListParams
from application.usecases import (
    ListProjectTasksElementResponse,
    ListProjectTasksRequest,
    ListProjectTasksUsecase,
)

logger = logging.getLogger(__name__)


class ListProjectTasksComposition:
    def __init__(self, unit_of_work: UnitOfWork, usecase: ListProjectTasksUsecase):
        self._unit_of_work = unit_of_work
        self._usecase = usecase

    async def __call__(
        self, request: ListProjectTasksRequest, params: ProjectTaskListParams
    ) -> list[ListProjectTasksElementResponse]:
        async with self._unit_of_work:
            logger.info("Listing tasks for project %s", request.project_id.value)
            response = await self._usecase(request, params)
        logger.info("Fetched %s tasks", len(response))
        return response
