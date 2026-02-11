__all__ = ["GrantOwnerComposition"]


import logging

from application.ports import UnitOfWork
from application.usecases import (
    SetMemberRoleRequest,
    SetMemberRoleUsecase,
    SetMemberRoleResponse,
)
from application.exceptions.handlers import retry_on_conflict


logger = logging.getLogger(__name__)


class SetMemberRoleComposition:

    def __init__(self, unit_of_work: UnitOfWork, usecase: SetMemberRoleUsecase):
        self._unit_of_work: UnitOfWork = unit_of_work
        self._usecase: SetMemberRoleUsecase = usecase

    @retry_on_conflict()
    async def __call__(self, request: SetMemberRoleRequest) -> SetMemberRoleResponse:
        async with self._unit_of_work:
            logger.info(
                "Role assignment request received: member=%s project=%s",
                request.user_id.value,
                request.project_id.value,
            )
            response: SetMemberRoleResponse = await self._usecase(request)
        logger.info(
            "Role assigned successfully: previous role=%s project=%s(%s)",
            response["old_role"],
            response["project"],
            request.project_id.value,
        )
        return response
