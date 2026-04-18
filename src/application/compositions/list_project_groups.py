import logging

from application.ports import UnitOfWork
from application.ports.gateways.query_params import ProjectGroupListParams
from application.usecases import (
    ListProjectGroupsElementResponse,
    ListProjectGroupsRequest,
    ListProjectGroupsUsecase,
)

logger = logging.getLogger(__name__)


class ListProjectGroupsComposition:
    def __init__(self, unit_of_work: UnitOfWork, usecase: ListProjectGroupsUsecase):
        self._unit_of_work = unit_of_work
        self._usecase = usecase

    async def __call__(
        self, request: ListProjectGroupsRequest, params: ProjectGroupListParams
    ) -> list[ListProjectGroupsElementResponse]:
        async with self._unit_of_work:
            logger.info("Listing groups for project %s", request.project_id.value)
            response = await self._usecase(request, params)
        logger.info("Fetched %s groups", len(response))
        return response
