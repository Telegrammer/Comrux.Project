from dataclasses import dataclass
from ..value_objects import PassedDatetime, FutureDatetime, Uuid4
from ..enums import TaskStatus
from .base import Entity


class TaskId(Uuid4): ...


@dataclass(kw_only=True)
class Task(Entity[TaskId]):
    """
    :raises DomainFieldError
    """

    task_type: str
    status: TaskStatus
    payload: dict
    created_at: PassedDatetime
    resend_time: FutureDatetime
    attempts: int
