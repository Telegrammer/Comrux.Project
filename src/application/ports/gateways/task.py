from abc import abstractmethod
from typing import Protocol, Sequence

from domain.entities import Task, TaskId
from .query_params import TaskListParams

__all__ = ["TaskCommandGateway", "TaskQueryGateway"]


class TaskCommandGateway(Protocol):

    @abstractmethod
    async def add(self, task: Task) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, task: Task) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, task: Task) -> None:
        raise NotImplementedError

    @abstractmethod
    async def claim_created_tasks(self, filters: TaskListParams) -> Sequence[Task]:
        raise NotImplementedError

    @abstractmethod
    async def mark_sent(self, task_id: TaskId) -> None:
        raise NotImplementedError


class TaskQueryGateway(Protocol):

    @abstractmethod
    async def by_id(self, task_id: TaskId) -> Task | None:
        raise NotImplementedError
