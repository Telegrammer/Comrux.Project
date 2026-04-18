import logging

from application.ports import UnitOfWork
from application.usecases import JoinProjectGroupRequest, JoinProjectGroupUsecase

logger = logging.getLogger(__name__)


class JoinProjectGroupComposition:
    def __init__(self, unit_of_work: UnitOfWork, usecase: JoinProjectGroupUsecase):
        self._unit_of_work = unit_of_work
        self._usecase = usecase

    async def __call__(self, request: JoinProjectGroupRequest) -> None:
        async with self._unit_of_work:
            logger.info(
                "Joining participant %s to group %s",
                request.participant_id.value,
                request.group_id.value,
            )
            await self._usecase(request)
        logger.info("Participant joined group")
