from dataclasses import dataclass
from typing import TypedDict

from application.ports.authorization import (
    CanCancelProjectTask,
    ProjectTaskCancelContext,
    authorize,
)
from application.ports import Clock
from application.ports.gateways import (
    ProjectQueryGateway,
    ProjectTaskCommandGateway,
    ProjectTaskQueryGateway,
)
from application.services import CurrentUserService
from domain.entities import ProjectTask, ProjectTaskId, UserId
from domain.enums import ProjectTaskStatus
from domain.services import ProjectTaskDomainService


@dataclass
class CancelProjectTaskRequest:
    task_id: ProjectTaskId

    @classmethod
    def from_primitives(cls, task_id: str) -> "CancelProjectTaskRequest":
        return cls(task_id=ProjectTaskId(task_id))


class CancelProjectTaskResponse(TypedDict):
    task_id: ProjectTaskId
    project_id: str
    status: ProjectTaskStatus

    @classmethod
    def from_entity(cls, task: ProjectTask) -> "CancelProjectTaskResponse":
        return cls(task_id=task.id_, project_id=task.project_id.value, status=task.status)


class CancelProjectTaskUsecase:
    def __init__(
        self,
        clock: Clock,
        current_user: CurrentUserService,
        project_queries: ProjectQueryGateway,
        task_queries: ProjectTaskQueryGateway,
        task_commands: ProjectTaskCommandGateway,
        task_service: ProjectTaskDomainService,
    ) -> None:
        self._clock = clock
        self._current_user = current_user
        self._project_queries = project_queries
        self._task_queries = task_queries
        self._task_commands = task_commands
        self._task_service = task_service

    async def __call__(self, request: CancelProjectTaskRequest) -> CancelProjectTaskResponse:
        current_user = await self._current_user()
        subject_id = UserId(current_user.id_)
        task = await self._task_queries.by_id(request.task_id)
        project = await self._project_queries.by_id(task.project_id.value)
        authorize(
            CanCancelProjectTask(),
            context=ProjectTaskCancelContext(
                subject_id=subject_id,
                subject_role=project.members.get(subject_id),
                task=task,
            ),
        )

        updated = self._task_service.change_status(
            task=task,
            new_status=ProjectTaskStatus.CANCELED,
            now=self._clock.now(),
        )
        await self._task_commands.update(updated)
        return CancelProjectTaskResponse.from_entity(updated)
