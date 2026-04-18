import logging

from application.ports import UnitOfWork
from application.usecases import (
    CreateProjectGroupRequest,
    CreateProjectGroupResponse,
    CreateProjectGroupUsecase,
)

logger = logging.getLogger(__name__)


class CreateProjectGroupComposition:
    def __init__(self, unit_of_work: UnitOfWork, usecase: CreateProjectGroupUsecase):
        self._unit_of_work = unit_of_work
        self._usecase = usecase

    async def __call__(
        self, request: CreateProjectGroupRequest
    ) -> CreateProjectGroupResponse:
        async with self._unit_of_work:
            logger.info(
                "Group creation started for project %s",
                request.project_id.value,
            )
            response = await self._usecase(request)
        logger.info("Group %s created", response["group_id"])
        return response
