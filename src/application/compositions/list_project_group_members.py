import logging

from application.ports import UnitOfWork, UserListParams
from application.usecases import (
    ListProjectGroupMembersElementResponse,
    ListProjectGroupMembersRequest,
    ListProjectGroupMembersUsecase,
)

logger = logging.getLogger(__name__)


class ListProjectGroupMembersComposition:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        usecase: ListProjectGroupMembersUsecase,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._usecase = usecase

    async def __call__(
        self,
        request: ListProjectGroupMembersRequest,
        params: UserListParams,
    ) -> list[ListProjectGroupMembersElementResponse]:
        async with self._unit_of_work:
            logger.info(
                "Fetching members of group %s in project %s",
                request.group_id.value,
                request.project_id.value,
            )
            response = await self._usecase(request, params)
        logger.info("Fetched %s members of project group", len(response))
        return response
