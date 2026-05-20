from dataclasses import dataclass
from typing import TypedDict

from application.ports.authorization import (
    CanCompleteProjectTask,
    ProjectTaskCompleteContext,
    authorize,
)
from application.ports import Clock
from application.ports.gateways import (
    ProjectGroupQueryGateway,
    ProjectQueryGateway,
    ProjectTaskCommandGateway,
    ProjectTaskQueryGateway,
)
from application.services import CurrentUserService
from domain.entities import (
    ProjectTask,
    ProjectTaskId,
    UserId,
)
from domain.enums import ProjectTaskStatus
from domain.services import ProjectTaskAssigneeAppliesVisitor, ProjectTaskDomainService


@dataclass
class CompleteProjectTaskRequest:
    task_id: ProjectTaskId

    @classmethod
    def from_primitives(cls, task_id: str) -> "CompleteProjectTaskRequest":
        return cls(task_id=ProjectTaskId(task_id))


class CompleteProjectTaskResponse(TypedDict):
    task_id: ProjectTaskId
    project_id: str
    status: ProjectTaskStatus

    @classmethod
    def from_entity(cls, task: ProjectTask) -> "CompleteProjectTaskResponse":
        return cls(task_id=task.id_, project_id=task.project_id.value, status=task.status)


class CompleteProjectTaskUsecase:
    def __init__(
        self,
        clock: Clock,
        current_user: CurrentUserService,
        project_queries: ProjectQueryGateway,
        project_group_queries: ProjectGroupQueryGateway,
        task_queries: ProjectTaskQueryGateway,
        task_commands: ProjectTaskCommandGateway,
        task_service: ProjectTaskDomainService,
    ) -> None:
        self._clock = clock
        self._current_user = current_user
        self._project_queries = project_queries
        self._project_group_queries = project_group_queries
        self._task_queries = task_queries
        self._task_commands = task_commands
        self._task_service = task_service

    async def __call__(
        self, request: CompleteProjectTaskRequest
    ) -> CompleteProjectTaskResponse:
        current_user = await self._current_user()
        subject_id = UserId(current_user.id_)
        task = await self._task_queries.by_id(request.task_id)
        project = await self._project_queries.by_id(task.project_id.value)
        subject_role = project.members.get(subject_id)
        subject_group_ids = await self._project_group_queries.group_ids_for_user(
            task.project_id, subject_id
        )

        applies_visitor = ProjectTaskAssigneeAppliesVisitor(
            user_id=subject_id,
            user_role=subject_role,
            user_group_ids=subject_group_ids,
        )
        authorize(
            CanCompleteProjectTask(),
            context=ProjectTaskCompleteContext(
                subject_id=subject_id,
                subject_role=subject_role,
                task=task,
                is_assigned=any(
                    assignee.accept(applies_visitor) for assignee in task.assignees
                ),
            ),
        )

        updated = self._task_service.change_status(
            task=task,
            new_status=ProjectTaskStatus.DONE,
            now=self._clock.now(),
        )
        await self._task_commands.update(updated)
        return CompleteProjectTaskResponse.from_entity(updated)
