from datetime import datetime, timedelta
from typing import Sequence

from domain.entities import Task, TaskId
from domain.value_objects import FutureDatetime, PassedDatetime
from domain.ports import TaskIdGenerator
from domain.enums import TaskStatus
from domain.policies import TaskPolicy
from domain.exceptions import DomainError


class TaskService:

    def __init__(self, id_generator: TaskIdGenerator, task_policy: TaskPolicy):
        self._id_generator = id_generator
        self._task_policy = task_policy

    def create_task(self, task_type: str, payload: dict, now: datetime) -> Task:

        return Task(
            id_=self._id_generator(),
            task_type=task_type,
            status=TaskStatus.CREATED,
            payload=payload,
            created_at=PassedDatetime(now, now),
            resend_time=FutureDatetime(now + self._task_policy.init_resend_delta, now),
            attempts=0,
        )

    def process_tasks(self, unprocessed_tasks: Sequence[Task]) -> list[Task]:
        return [self.process_task(task) for task in unprocessed_tasks]

    def process_task(self, task: Task) -> Task:

        if task.status != TaskStatus.PROCESSING:
            raise DomainError("Task must be in processing status")

        return Task(
            id_=TaskId(task.id_),
            task_type=task.task_type,
            status=TaskStatus.SENT,
            payload=task.payload,
            created_at=task.created_at,
            resend_time=task.resend_time,
            attempts=task.attempts + 1,
        )

    def retry_task(self, task: Task, now: datetime) -> Task:

        if task.status != TaskStatus.PROCESSING:
            raise DomainError("Task must be in processing status")

        new_status: TaskStatus = (
            TaskStatus.CREATED
            if task.attempts < self._task_policy.max_attempt_count
            else TaskStatus.FAILED
        )

        return Task(
            id_=TaskId(task.id_),
            task_type=task.task_type,
            status=new_status,
            payload=task.payload,
            created_at=PassedDatetime(task.created_at, now),
            resend_time=FutureDatetime(
                now + timedelta(seconds=2**task.attempts), task.resend_time
            ),
            attempts=task.attempts + 1,
        )
