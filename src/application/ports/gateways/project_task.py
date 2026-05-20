from abc import abstractmethod
from datetime import datetime
from typing import Protocol, Sequence

from application.models import ProjectTaskDetailsRead
from domain.entities import ProjectId, ProjectTask, ProjectTaskId

from .query_params import ProjectTaskListParams


class ProjectTaskCommandGateway(Protocol):
    @abstractmethod
    async def add(self, task: ProjectTask) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, task: ProjectTask) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update_many(self, tasks: Sequence[ProjectTask]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def sync_overdue_batch(self, project_id: ProjectId, now: datetime) -> int:
        raise NotImplementedError


class ProjectTaskQueryGateway(Protocol):
    @abstractmethod
    async def by_id(self, task_id: ProjectTaskId) -> ProjectTask:
        raise NotImplementedError

    @abstractmethod
    async def by_id_detailed(self, task_id: ProjectTaskId) -> ProjectTaskDetailsRead:
        raise NotImplementedError

    @abstractmethod
    async def by_project(
        self, project_id: ProjectId, params: ProjectTaskListParams
    ) -> Sequence[ProjectTask]:
        raise NotImplementedError
