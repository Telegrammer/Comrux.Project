import logging

from application.ports import Clock, TaskCommandGateway, UnitOfWork
from application.usecases import (
    SetProjectTaskStatusRequest,
    SetProjectTaskStatusResponse,
    SetProjectTaskStatusUsecase,
)
from domain.services import TaskService

logger = logging.getLogger(__name__)


class SetProjectTaskStatusComposition:
    _task_type = "project.task.status_changed"

    def __init__(
        self,
        clock: Clock,
        unit_of_work: UnitOfWork,
        usecase: SetProjectTaskStatusUsecase,
        outbox_task_service: TaskService,
        outbox_task_gateway: TaskCommandGateway,
    ):
        self._clock = clock
        self._unit_of_work = unit_of_work
        self._usecase = usecase
        self._outbox_task_service = outbox_task_service
        self._outbox_task_gateway = outbox_task_gateway

    async def __call__(
        self, request: SetProjectTaskStatusRequest
    ) -> SetProjectTaskStatusResponse:
        async with self._unit_of_work:
            logger.info("Task status update started for task %s", request.task_id.value)
            response = await self._usecase(request)
            await self._outbox_task_gateway.add(
                self._outbox_task_service.create_task(
                    self._task_type,
                    {
                        "project_id": response["project_id"],
                        "task_id": str(response["task_id"]),
                        "status": response["status"].value,
                        "title": response["title"],
                    },
                    now=self._clock.now(),
                )
            )
        logger.info("Task %s moved to %s", response["task_id"], response["status"])
        return response
