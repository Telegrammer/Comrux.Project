__all__ = ["RemoveProjectMemberComposition"]


import logging

from domain.entities import Task
from domain.services import TaskService
from application.ports import UnitOfWork, Clock, TaskCommandGateway
from application.usecases import (
    RemoveProjectMemberRequest,
    RemoveProjectMemberUsecase,
    RemoveProjectMemberResponse,
)
from application.exceptions.handlers import retry_on_conflict


logger = logging.getLogger(__name__)


class RemoveProjectMemberComposition:
    def __init__(
        self,
        clock: Clock,
        task_service: TaskService,
        task_gateway: TaskCommandGateway,
        unit_of_work: UnitOfWork,
        usecase: RemoveProjectMemberUsecase,
    ):
        self._clock = clock
        self._task_service = task_service
        self._task_gateway = task_gateway
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

            task: Task = self._task_service.create_task(
                "project.member_removed",
                {
                    "project_id": request.project_id.value,
                    "member_id": request.user_id.value,
                },
                self._clock.now(),
            )
            await self._task_gateway.add(task)

        logger.info(
            "User %s successfully removed from project %s (%s)",
            response["member"],
            response["project"],
            request.project_id.value,
        )
        return response
