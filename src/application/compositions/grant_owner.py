__all__ = ["GrantOwnerComposition"]


import logging

from application.ports import UnitOfWork
from application.usecases import (
    GrantOwnerRequest,
    GrantOwnerUsecase,
    GrantOwnerResponse,
)


logger = logging.getLogger(__name__)


class GrantOwnerComposition:

    def __init__(self, unit_of_work: UnitOfWork, usecase: GrantOwnerUsecase):
        self._unit_of_work: UnitOfWork = unit_of_work
        self._usecase: GrantOwnerUsecase = usecase

    async def __call__(self, request: GrantOwnerRequest) -> GrantOwnerResponse:
        async with self._unit_of_work:
            logger.info(
                "Ownership transfer request received: requester=%s project=%s",
                request.user_id.value,
                request.project_id.value,
            )
            response: GrantOwnerResponse = await self._usecase(request)
        logger.info(
            "Ownership transferred successfully: previous_owner=%s(%s) project=%s(%s)",
            response["old_owner_name"],
            response["old_owner_id"],
            response["project"],
            request.project_id.value,
        )
        return response
