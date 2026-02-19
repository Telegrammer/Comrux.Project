from abc import abstractmethod
from typing import Protocol
from dataclasses import dataclass
from domain.entities import Task, TaskId


@dataclass
class TaskSendResult:
    success: bool


class TaskNotifier(Protocol):

    @abstractmethod
    def notify(self, task: Task) -> TaskSendResult:
        raise NotImplementedError

    @abstractmethod
    def notify_batch(self, batch: list[Task]) -> dict[TaskId, TaskSendResult]:
        raise NotImplementedError
