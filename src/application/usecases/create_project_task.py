from dataclasses import dataclass
from datetime import datetime
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
)
from application.services import CurrentUserService
from domain.entities import (
    ProjectTask,
    ProjectTaskAssignee,
    ProjectTaskId,
    ProjectId,
    UserId,
)
from domain.services import ProjectTaskDomainService


@dataclass
class CreateProjectTaskRequest:
    project_id: ProjectId
    title: str
    description: str
    start_at: datetime
    end_at: datetime
    assignees: list[ProjectTaskAssignee]

    @classmethod
    def from_primitives(
        cls,
        project_id: str,
        title: str,
        description: str,
        start_at: datetime,
        end_at: datetime,
        assignees: list[ProjectTaskAssignee] | None = None,
    ) -> "CreateProjectTaskRequest":
        return cls(
            project_id=ProjectId(project_id),
            title=title,
            description=description,
            start_at=start_at,
            end_at=end_at,
            assignees=assignees or [],
        )


class CreateProjectTaskResponse(TypedDict):
    task_id: ProjectTaskId
    project_id: ProjectId
    title: str

    @classmethod
    def from_entity(cls, task: ProjectTask) -> "CreateProjectTaskResponse":
        return cls(task_id=task.id_, project_id=task.project_id, title=task.title)


class CreateProjectTaskUsecase:
    def __init__(
        self,
        current_user: CurrentUserService,
        project_queries: ProjectQueryGateway,
        task_commands: ProjectTaskCommandGateway,
        task_service: ProjectTaskDomainService,
        clock: Clock,
    ) -> None:
        self._current_user = current_user
        self._project_queries = project_queries
        self._task_commands = task_commands
        self._task_service = task_service
        self._clock = clock

    async def __call__(
        self, request: CreateProjectTaskRequest
    ) -> CreateProjectTaskResponse:
        project = await self._project_queries.by_id(request.project_id.value)
        current_user = await self._current_user()
        subject_id = UserId(current_user.id_)
        authorize(
            CanManageProjectTask(),
            context=ProjectManagmentContext(
                subject=current_user,
                target=project,
            ),
        )

        now = self._clock.now()
        task = self._task_service.create_task(
            project_id=ProjectId(project.id_),
            creator_id=subject_id,
            title=request.title,
            description=request.description,
            start_at=self._clock.normalize(request.start_at),
            end_at=self._clock.normalize(request.end_at),
            now=now,
        )
        for assignee in request.assignees:
            task = self._task_service.assign(task=task, assignee=assignee, now=now)

        await self._task_commands.add(task)
        return CreateProjectTaskResponse.from_entity(task)
