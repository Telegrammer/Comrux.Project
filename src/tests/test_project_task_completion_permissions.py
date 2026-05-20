from datetime import datetime

from application.ports.authorization import (
    CanCancelProjectTask,
    CanCompleteProjectTask,
    ProjectTaskCancelContext,
    ProjectTaskCompleteContext,
)
from domain.entities import (
    ProjectId,
    ProjectTask,
    ProjectTaskId,
    ProjectTaskGroupAssignee,
    ProjectTaskRoleAssignee,
    ProjectTaskUserAssignee,
    UserId,
)
from domain.entities.project_group import ProjectGroupId
from domain.enums import ProjectRole, ProjectTaskStatus
from domain.services import ProjectTaskAssigneeAppliesVisitor


def _task(*, assignees: list) -> ProjectTask:
    now = datetime(2026, 4, 28, 10, 0, 0)
    return ProjectTask(
        id_=ProjectTaskId("550e8400-e29b-41d4-a716-446655440101"),
        project_id=ProjectId("550e8400-e29b-41d4-a716-446655440102"),
        title="Task",
        description="Desc",
        status=ProjectTaskStatus.IN_PROGRESS,
        creator_id=UserId("550e8400-e29b-41d4-a716-446655440103"),
        start_at=now,
        end_at=now.replace(hour=12),
        created_at=now,
        updated_at=now,
        assignees=assignees,
    )


def test_assignee_applies_visitor_matches_user_role_and_group() -> None:
    user_id = UserId("550e8400-e29b-41d4-a716-446655440104")
    group_id = ProjectGroupId("550e8400-e29b-41d4-a716-446655440105")
    visitor = ProjectTaskAssigneeAppliesVisitor(
        user_id=user_id,
        user_role=ProjectRole.MEMBER,
        user_group_ids=frozenset({group_id}),
    )

    assert ProjectTaskUserAssignee(user_id.value).accept(visitor) is True
    assert ProjectTaskRoleAssignee(ProjectRole.MEMBER).accept(visitor) is True
    assert ProjectTaskGroupAssignee(group_id).accept(visitor) is True


def test_can_complete_project_task_requires_creator_owner_or_assignee() -> None:
    permission = CanCompleteProjectTask()
    subject_id = UserId("550e8400-e29b-41d4-a716-446655440106")
    task = _task(assignees=[])

    denied = permission.is_satisfied_by(
        ProjectTaskCompleteContext(
            subject_id=subject_id,
            subject_role=ProjectRole.MEMBER,
            task=task,
            is_assigned=False,
        )
    )
    allowed = permission.is_satisfied_by(
        ProjectTaskCompleteContext(
            subject_id=subject_id,
            subject_role=ProjectRole.MEMBER,
            task=task,
            is_assigned=True,
        )
    )

    assert denied.success is False
    assert allowed.success is True


def test_can_cancel_project_task_allows_only_creator_or_owner() -> None:
    permission = CanCancelProjectTask()
    task = _task(assignees=[])

    creator_allowed = permission.is_satisfied_by(
        ProjectTaskCancelContext(
            subject_id=task.creator_id,
            subject_role=ProjectRole.MEMBER,
            task=task,
        )
    )
    owner_allowed = permission.is_satisfied_by(
        ProjectTaskCancelContext(
            subject_id=UserId("550e8400-e29b-41d4-a716-446655440107"),
            subject_role=ProjectRole.OWNER,
            task=task,
        )
    )
    denied = permission.is_satisfied_by(
        ProjectTaskCancelContext(
            subject_id=UserId("550e8400-e29b-41d4-a716-446655440108"),
            subject_role=ProjectRole.MEMBER,
            task=task,
        )
    )

    assert creator_allowed.success is True
    assert owner_allowed.success is True
    assert denied.success is False
