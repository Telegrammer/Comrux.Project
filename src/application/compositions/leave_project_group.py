import logging

from application.ports import UnitOfWork
from application.usecases import LeaveProjectGroupRequest, LeaveProjectGroupUsecase

logger = logging.getLogger(__name__)


class LeaveProjectGroupComposition:
    def __init__(self, unit_of_work: UnitOfWork, usecase: LeaveProjectGroupUsecase):
        self._unit_of_work = unit_of_work
        self._usecase = usecase

    async def __call__(self, request: LeaveProjectGroupRequest) -> None:
        async with self._unit_of_work:
            logger.info(
                "Removing participant %s from group %s",
                request.participant_id.value,
                request.group_id.value,
            )
            await self._usecase(request)
        logger.info("Participant removed from group")
