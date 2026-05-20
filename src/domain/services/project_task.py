from __future__ import annotations

from datetime import datetime

from domain.entities import (
    ProjectTask,
    ProjectTaskAssignee,
    ProjectTaskGroupAssignee,
    ProjectTaskId,
    ProjectTaskRoleAssignee,
    ProjectTaskUserAssignee,
    ProjectId,
    UserId,
)
from domain.entities.project_group import ProjectGroupId
from domain.enums import ProjectRole, ProjectTaskStatus
from domain.exceptions import (
    ProjectTaskAssigneeContextError,
    ProjectTaskInvalidStatusTransitionError,
)
from domain.ports import ProjectTaskIdGenerator


class ProjectTaskDomainService:
    _allowed_transitions: dict[ProjectTaskStatus, set[ProjectTaskStatus]] = {
        ProjectTaskStatus.PLANNED: {
            ProjectTaskStatus.IN_PROGRESS,
            ProjectTaskStatus.CANCELED,
        },
        ProjectTaskStatus.IN_PROGRESS: {
            ProjectTaskStatus.DONE,
            ProjectTaskStatus.OVERDUE,
            ProjectTaskStatus.CANCELED,
        },
        ProjectTaskStatus.OVERDUE: {ProjectTaskStatus.CANCELED},
        ProjectTaskStatus.DONE: set(),
        ProjectTaskStatus.CANCELED: set(),
    }

    def __init__(self, id_generator: ProjectTaskIdGenerator) -> None:
        self._id_generator = id_generator

    @staticmethod
    def _read_vo[T](entity: object, *, hidden_attr: str, public_attr: str, vo_type: type[T]) -> T:
        hidden_value = getattr(entity, hidden_attr, None)
        if hidden_value is not None:
            return hidden_value

        value = getattr(entity, public_attr)
        if isinstance(value, vo_type):
            return value
        return vo_type(value)

    @staticmethod
    def _clone_task(
        task: ProjectTask,
        *,
        status: ProjectTaskStatus | None = None,
        assignees: list[ProjectTaskAssignee] | None = None,
        updated_at: datetime | None = None,
    ) -> ProjectTask:
        task_id = ProjectTaskDomainService._read_vo(
            task,
            hidden_attr="__object_id_",
            public_attr="id_",
            vo_type=ProjectTaskId,
        )
        project_id = ProjectTaskDomainService._read_vo(
            task,
            hidden_attr="__object_project_id",
            public_attr="project_id",
            vo_type=ProjectId,
        )
        creator_id = ProjectTaskDomainService._read_vo(
            task,
            hidden_attr="__object_creator_id",
            public_attr="creator_id",
            vo_type=UserId,
        )

        return ProjectTask(
            id_=task_id,
            project_id=project_id,
            title=task.title,
            description=task.description,
            status=task.status if status is None else status,
            creator_id=creator_id,
            start_at=task.start_at,
            end_at=task.end_at,
            created_at=task.created_at,
            updated_at=task.updated_at if updated_at is None else updated_at,
            assignees=task.assignees if assignees is None else assignees,
        )

    def create_task(
        self,
        *,
        project_id: ProjectId,
        creator_id: UserId,
        title: str,
        description: str,
        start_at: datetime,
        end_at: datetime,
        now: datetime,
    ) -> ProjectTask:
        return ProjectTask(
            id_=self._id_generator(),
            project_id=project_id,
            title=title,
            description=description,
            status=(
                ProjectTaskStatus.PLANNED
                if start_at > now
                else ProjectTaskStatus.IN_PROGRESS
            ),
            creator_id=creator_id,
            start_at=start_at,
            end_at=end_at,
            created_at=now,
            updated_at=now,
            assignees=[],
        )

    def assign(
        self,
        *,
        task: ProjectTask,
        assignee: ProjectTaskAssignee,
        now: datetime,
    ) -> ProjectTask:
        if assignee in task.assignees:
            raise ProjectTaskAssigneeContextError("Task already has the same assignee")

        return self._clone_task(
            task,
            assignees=[*task.assignees, assignee],
            updated_at=now,
        )

    def change_status(
        self,
        *,
        task: ProjectTask,
        new_status: ProjectTaskStatus,
        now: datetime,
    ) -> ProjectTask:
        if new_status not in self._allowed_transitions[task.status]:
            raise ProjectTaskInvalidStatusTransitionError(
                f"Transition {task.status.value} -> {new_status.value} is not allowed"
            )
        return self._clone_task(task, status=new_status, updated_at=now)

    def sync_overdue(self, *, task: ProjectTask, now: datetime) -> ProjectTask:
        if task.status in {ProjectTaskStatus.DONE, ProjectTaskStatus.CANCELED}:
            return task
        if task.end_at <= now and task.status != ProjectTaskStatus.OVERDUE:
            return self._clone_task(
                task, status=ProjectTaskStatus.OVERDUE, updated_at=now
            )
        return task

    def restore_status_from_time(
        self, *, task: ProjectTask, now: datetime
    ) -> ProjectTask:
        if task.status in {
            ProjectTaskStatus.DONE,
            ProjectTaskStatus.CANCELED,
            ProjectTaskStatus.OVERDUE,
        }:
            return task
        next_status = (
            ProjectTaskStatus.PLANNED
            if task.start_at > now
            else ProjectTaskStatus.IN_PROGRESS
        )
        return self._clone_task(task, status=next_status, updated_at=now)


class ProjectTaskAssigneeAppliesVisitor:
    def __init__(
        self,
        *,
        user_id: UserId,
        user_role: ProjectRole | None,
        user_group_ids: frozenset[ProjectGroupId],
    ) -> None:
        self._user_id = user_id
        self._user_role = user_role
        self._user_group_ids = user_group_ids

    def visit_user(self, assignee: ProjectTaskUserAssignee) -> bool:
        return assignee.user_id == self._user_id

    def visit_role(self, assignee: ProjectTaskRoleAssignee) -> bool:
        return self._user_role is not None and assignee.role == self._user_role

    def visit_group(self, assignee: ProjectTaskGroupAssignee) -> bool:
        return assignee.group_id in self._user_group_ids
