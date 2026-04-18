import logging

from application.ports import UnitOfWork
from application.usecases import DeleteProjectGroupRequest, DeleteProjectGroupUsecase

logger = logging.getLogger(__name__)


class DeleteProjectGroupComposition:
    def __init__(self, unit_of_work: UnitOfWork, usecase: DeleteProjectGroupUsecase):
        self._unit_of_work = unit_of_work
        self._usecase = usecase

    async def __call__(self, request: DeleteProjectGroupRequest) -> None:
        async with self._unit_of_work:
            logger.info("Group %s deletion started", request.group_id.value)
            await self._usecase(request)
        logger.info("Group deleted")
