import logging

from application.ports import UnitOfWork, ProjectListParams
from application.usecases import (
    ListProjectsUsecase,
    ListProjectsElementResponse,
)


logger = logging.getLogger(__name__)


class ListProjectsComposition:

    def __init__(self, unit_of_work: UnitOfWork, usecase: ListProjectsUsecase):
        self._unit_of_work: UnitOfWork = unit_of_work
        self._usecase: ListProjectsUsecase = usecase

    async def __call__(
        self, search_params: ProjectListParams
    ) -> list[ListProjectsElementResponse]:
        async with self._unit_of_work:
            logger.info(
                "Fetching projects from %s to %s",
                search_params.pagination.offset,
                search_params.pagination.offset + search_params.pagination.limit,
            )
            response: list[ListProjectsElementResponse] = await self._usecase(
                search_params
            )
        logger.info(
            "Successfully fetched %s projects",
            len(response),
        )
        return response
