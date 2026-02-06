__all__ = ["ListProjectMembersComposition"]


import logging

from application.ports import UnitOfWork, UserListParams
from application.usecases import (
    ListProjectMembersRequest,
    ListProjectMembersUsecase,
    ListProjectMembersElementResponse,
)


logger = logging.getLogger(__name__)


class ListProjectMembersComposition:

    def __init__(self, unit_of_work: UnitOfWork, usecase: ListProjectMembersUsecase):
        self._unit_of_work: UnitOfWork = unit_of_work
        self._usecase: ListProjectMembersUsecase = usecase

    async def __call__(
        self, request: ListProjectMembersRequest, search_params: UserListParams
    ) -> list[ListProjectMembersElementResponse]:
        async with self._unit_of_work:
            logger.info(
                "Fetching members of project %s",
                request.project_id.value,
            )
            response: list[ListProjectMembersElementResponse] = await self._usecase(
                request, search_params
            )
        logger.info(
            "Successfully fetched %s members of project %s",
            len(response),
            request.project_id.value,
        )
        return response
