from dataclasses import dataclass
from typing import TypedDict

from application.ports.authorization import (
    CanManageProjectTask,
    ProjectManagmentContext,
    authorize,
)
from application.ports import Clock
from application.ports.gateways import (
    ProjectQueryGateway,
    ProjectTaskCommandGateway,
    ProjectTaskQueryGateway,
)
from application.services import CurrentUserService
from domain.entities import ProjectTask, ProjectTaskId
from domain.enums import ProjectTaskStatus
from domain.services import ProjectTaskDomainService


@dataclass
class SetProjectTaskStatusRequest:
    task_id: ProjectTaskId
    status: ProjectTaskStatus

    @classmethod
    def from_primitives(
        cls, task_id: str, status: str
    ) -> "SetProjectTaskStatusRequest":
        return cls(task_id=ProjectTaskId(task_id), status=ProjectTaskStatus(status))


class SetProjectTaskStatusResponse(TypedDict):
    task_id: ProjectTaskId
    project_id: str
    status: ProjectTaskStatus
    title: str

    @classmethod
    def from_entity(cls, task: ProjectTask) -> "SetProjectTaskStatusResponse":
        return cls(
            task_id=task.id_,
            project_id=task.project_id.value,
            status=task.status,
            title=task.title,
        )


class SetProjectTaskStatusUsecase:
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

    async def __call__(
        self, request: SetProjectTaskStatusRequest
    ) -> SetProjectTaskStatusResponse:
        current_user = await self._current_user()
        task = await self._task_queries.by_id(request.task_id.value)
        project = await self._project_queries.by_id(task.project_id.value)
        authorize(
            CanManageProjectTask(),
            context=ProjectManagmentContext(subject=current_user, target=project),
        )
        updated = self._task_service.change_status(
            task=task, new_status=request.status, now=self._clock.now()
        )
        await self._task_commands.update(updated)
        return SetProjectTaskStatusResponse.from_entity(updated)
