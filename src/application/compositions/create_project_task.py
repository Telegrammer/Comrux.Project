import logging

from application.ports import Clock, TaskCommandGateway, UnitOfWork
from application.usecases import (
    CreateProjectTaskRequest,
    CreateProjectTaskResponse,
    CreateProjectTaskUsecase,
)
from domain.services import TaskService

logger = logging.getLogger(__name__)


class CreateProjectTaskComposition:
    _task_type = "project.task.created"

    def __init__(
        self,
        clock: Clock,
        unit_of_work: UnitOfWork,
        usecase: CreateProjectTaskUsecase,
        outbox_task_service: TaskService,
        outbox_task_gateway: TaskCommandGateway,
    ):
        self._clock = clock
        self._unit_of_work = unit_of_work
        self._usecase = usecase
        self._outbox_task_service = outbox_task_service
        self._outbox_task_gateway = outbox_task_gateway

    async def __call__(self, request: CreateProjectTaskRequest) -> CreateProjectTaskResponse:
        async with self._unit_of_work:
            logger.info("Task creation started for project %s", request.project_id.value)
            response = await self._usecase(request)
            await self._outbox_task_gateway.add(
                self._outbox_task_service.create_task(
                    self._task_type,
                    {
                        "project_id": response["project_id"].value,
                        "task_id": str(response["task_id"]),
                        "title": response["title"],
                    },
                    now=self._clock.now(),
                )
            )
        logger.info("Task %s created", response["task_id"])
        return response
