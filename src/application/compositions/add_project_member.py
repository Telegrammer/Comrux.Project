__all__ = ["AddProjectMemberComposition"]


import logging

from application.ports import UnitOfWork
from application.usecases import (
    AddProjectMemberRequest,
    AddProjectMemberUsecase,
    AddProjectMemberResponse,
)
from application.exceptions.handlers import retry_on_conflict


logger = logging.getLogger(__name__)


class AddProjectMemberComposition:

    def __init__(self, unit_of_work: UnitOfWork, usecase: AddProjectMemberUsecase):
        self._unit_of_work: UnitOfWork = unit_of_work
        self._usecase: AddProjectMemberUsecase = usecase

    @retry_on_conflict()
    async def __call__(
        self, request: AddProjectMemberRequest
    ) -> AddProjectMemberResponse:
        async with self._unit_of_work:
            logger.info(
                "Start adding user %s to project %s",
                request.user_id.value,
                request.project_id.value,
            )
            response = await self._usecase(request)
        logger.info(
            "User %s (%s) successfully added to project %s (%s)",
            response["member"],
            request.user_id.value,
            response["project"],
            request.project_id.value,
        )
        return response
