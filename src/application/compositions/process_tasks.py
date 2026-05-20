import logging
from typing import Sequence
from datetime import datetime
from domain.entities import Task, TaskId
from domain.services import TaskService
from application.ports import (
    TaskCommandGateway,
    TaskNotifier,
    TaskSendResult,
    UnitOfWork,
    Clock,
)
from application.ports.gateways.query_params import TaskListParams


logger = logging.getLogger(__name__)


class ProcessTasksComposition:
    def __init__(
        self,
        clock: Clock,
        unit_of_work: UnitOfWork,
        task_service: TaskService,
        commands: TaskCommandGateway,
        notifier: TaskNotifier,
    ):
        self._unit_of_work = unit_of_work
        self._clock = clock
        self._task_service: TaskService = task_service
        self._commands: TaskCommandGateway = commands
        self._notifier: TaskNotifier = notifier

    async def __call__(self, search_params: TaskListParams) -> None:

        async with self._unit_of_work:
            unprocessed_tasks: Sequence[
                Task
            ] = await self._commands.claim_created_tasks(search_params)

        if not unprocessed_tasks:
            return

        logging.info(
            "Found new tasks with resend time less then %s",
            search_params.current_resend_time,
        )

        processed_tasks: list[Task] = self._task_service.process_tasks(
            unprocessed_tasks
        )

        send_results: dict[TaskId, TaskSendResult] = await self._notifier.notify_batch(
            processed_tasks
        )

        now: datetime = self._clock.now()

        async with self._unit_of_work:
            for task in processed_tasks:
                result: TaskSendResult = send_results.get(task.id_)

                if result and result.success:
                    await self._commands.mark_sent(task.id_)
                    logger.info("Task %s was sent", task.id_)
                    continue

                retry_task: Task = self._task_service.retry_task(task, now)
                await self._commands.update(retry_task)
                logger.warning("Task %s sending failed", task.id_)

        logger.info("Task proccesed.")
