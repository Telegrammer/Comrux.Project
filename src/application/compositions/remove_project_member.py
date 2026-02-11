__all__ = ["RemoveProjectMemberComposition"]


import logging

from application.ports import UnitOfWork
from application.usecases import (
    RemoveProjectMemberRequest,
    RemoveProjectMemberUsecase,
    RemoveProjectMemberResponse,
)
from application.exceptions.handlers import retry_on_conflict


logger = logging.getLogger(__name__)


class RemoveProjectMemberComposition:

    def __init__(self, unit_of_work: UnitOfWork, usecase: RemoveProjectMemberUsecase):
        self._unit_of_work: UnitOfWork = unit_of_work
        self._usecase: RemoveProjectMemberUsecase = usecase

    @retry_on_conflict()
    async def __call__(
        self, request: RemoveProjectMemberRequest
    ) -> RemoveProjectMemberResponse:
        async with self._unit_of_work:
            logger.info(
                "Start removing user %s from project %s",
                request.user_id.value,
                request.project_id.value,
            )
            response = await self._usecase(request)
        logger.info(
            "User %s successfully removed from project %s (%s)",
            response["member"],
            response["project"],
            request.project_id.value,
        )
        return response
