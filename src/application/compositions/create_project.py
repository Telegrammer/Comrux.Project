__all__ = [
    "CreateProjectComposition",
]


import logging

from domain.entities import Task
from domain.services import TaskService
from application.ports import UnitOfWork, TaskCommandGateway, Clock
from application.usecases import (
    CreateProjectRequest,
    CreateProjectUsecase,
    CreateProjectResponse,
)

logger = logging.getLogger(__name__)


class CreateProjectComposition:
    def __init__(
        self,
        clock: Clock,
        usecase: CreateProjectUsecase,
        unit_of_work: UnitOfWork,
        task_gateway: TaskCommandGateway,
        task_service: TaskService,
    ):
        self._clock = clock
        self._usecase: CreateProjectUsecase = usecase
        self._unit_of_work: UnitOfWork = unit_of_work
        self._taks_gateway = task_gateway
        self._task_service = task_service

    async def __call__(self, request: CreateProjectRequest) -> CreateProjectResponse:
        async with self._unit_of_work:
            logger.info("Project creation started")
            response: CreateProjectResponse = await self._usecase(request)

            task: Task = self._task_service.create_task(
                "project.created",
                {
                    "project_id": response["project_id"],
                    "owner_id": response["owner_id"],
                },
                self._clock.now(),
            )
            await self._taks_gateway.add(task)

        logger.info("Project %s was created", response["project_id"])
        return response
