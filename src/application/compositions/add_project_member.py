__all__ = ["AddProjectMemberComposition"]


import logging

from domain.entities import Task
from domain.services import TaskService
from application.ports import UnitOfWork, TaskCommandGateway, Clock
from application.usecases import (
    AddProjectMemberRequest,
    AddProjectMemberUsecase,
    AddProjectMemberResponse,
)
from application.exceptions.handlers import retry_on_conflict


logger = logging.getLogger(__name__)


class AddProjectMemberComposition:
    def __init__(
        self,
        clock: Clock,
        task_service: TaskService,
        task_gateway: TaskCommandGateway,
        unit_of_work: UnitOfWork,
        usecase: AddProjectMemberUsecase,
    ):
        self._clock = clock
        self._task_service = task_service
        self._task_gateway = task_gateway
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

            task: Task = self._task_service.create_task(
                "project.member_added",
                {"project_id": request.project_id.value, "member_id": request.user_id.value},
                self._clock.now(),
            )
            await self._task_gateway.add(task)

        logger.info(
            "User %s (%s) successfully added to project %s (%s)",
            response["member"],
            request.user_id.value,
            response["project"],
            request.project_id.value,
        )
        return response
