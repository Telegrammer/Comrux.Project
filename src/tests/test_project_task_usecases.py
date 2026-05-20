import asyncio
from datetime import datetime
from types import SimpleNamespace

import pytest

from application.exceptions import AccessDeniedError
from application.usecases import (
    AssignProjectTaskUsecase,
    CreateProjectTaskRequest,
    CreateProjectTaskUsecase,
)
from domain.entities import (
    ProjectGroupId,
    ProjectId,
    ProjectTaskGroupAssignee,
    ProjectTaskId,
    ProjectTaskRoleAssignee,
    ProjectTaskUserAssignee,
    UserId,
)
from domain.enums import ProjectRole
from domain.services import ProjectTaskDomainService


class ClockStub:
    def __init__(self, now):
        self._now = now

    def now(self):
        return self._now


class CurrentUserStub:
    def __init__(self, user_id: str) -> None:
        self._user = SimpleNamespace(id_=user_id)

    async def __call__(self):
        return self._user


class ProjectQueriesStub:
    def __init__(self, project):
        self._project = project

    async def by_id(self, _project_id: str):
        return self._project


class ProjectGroupQueriesStub:
    def __init__(self):
        self._groups: dict[ProjectGroupId, object] = {}
        self._memberships: dict[tuple[str, str], frozenset[ProjectGroupId]] = {}

    async def by_id(self, group_id: ProjectGroupId):
        return self._groups[group_id]

    async def group_ids_for_user(
        self, project_id: ProjectId, user_id: UserId
    ) -> frozenset[ProjectGroupId]:
        return self._memberships.get((project_id.value, user_id.value), frozenset())


class TaskCommandsStub:
    def __init__(self) -> None:
        self.added_task = None

    async def add(self, task) -> None:
        self.added_task = task


class ProjectTaskIdGeneratorStub:
    def __call__(self):
        return ProjectTaskId("550e8400-e29b-41d4-a716-446655440090")


def test_create_project_task_denies_member() -> None:
    async def scenario() -> None:
        now = datetime(2026, 4, 26, 10, 0, 0)
        current_user_id = UserId("550e8400-e29b-41d4-a716-446655440010")
        project = SimpleNamespace(
            id_="550e8400-e29b-41d4-a716-446655440011",
            members={current_user_id: ProjectRole.MEMBER},
        )
        usecase = CreateProjectTaskUsecase(
            current_user=CurrentUserStub(current_user_id.value),
            project_queries=ProjectQueriesStub(project),
            task_commands=TaskCommandsStub(),
            task_service=ProjectTaskDomainService(ProjectTaskIdGeneratorStub()),
            clock=ClockStub(now),
        )

        with pytest.raises(AccessDeniedError):
            await usecase(
                CreateProjectTaskRequest.from_primitives(
                    project_id=project.id_,
                    title="Prepare KPI",
                    description="Build weekly KPI summary",
                    start_at=now,
                    end_at=now.replace(hour=12),
                    assignees=[],
                )
            )

    asyncio.run(scenario())


def test_create_project_task_allows_lead_without_assignees() -> None:
    async def scenario() -> None:
        now = datetime(2026, 4, 26, 10, 0, 0)
        current_user_id = UserId("550e8400-e29b-41d4-a716-446655440020")
        project = SimpleNamespace(
            id_="550e8400-e29b-41d4-a716-446655440021",
            members={current_user_id: ProjectRole.LEAD},
        )
        task_commands = TaskCommandsStub()
        usecase = CreateProjectTaskUsecase(
            current_user=CurrentUserStub(current_user_id.value),
            project_queries=ProjectQueriesStub(project),
            task_commands=task_commands,
            task_service=ProjectTaskDomainService(ProjectTaskIdGeneratorStub()),
            clock=ClockStub(now),
        )

        response = await usecase(
            CreateProjectTaskRequest.from_primitives(
                project_id=project.id_,
                title="Prepare roadmap",
                description="Draft project roadmap",
                start_at=now,
                end_at=now.replace(hour=11),
                assignees=[],
            )
        )

        assert response["project_id"].value == project.id_
        assert task_commands.added_task is not None
        assert task_commands.added_task.title == "Prepare roadmap"

    asyncio.run(scenario())


def test_assign_role_denies_member_subject() -> None:
    async def scenario() -> None:
        now = datetime(2026, 4, 26, 10, 0, 0)
        current_user_id = UserId("550e8400-e29b-41d4-a716-446655440030")
        project = SimpleNamespace(
            id_="550e8400-e29b-41d4-a716-446655440031",
            members={current_user_id: ProjectRole.MEMBER},
        )
        task_commands = TaskCommandsStub()
        create_usecase = CreateProjectTaskUsecase(
            current_user=CurrentUserStub(current_user_id.value),
            project_queries=ProjectQueriesStub(project),
            task_commands=task_commands,
            task_service=ProjectTaskDomainService(ProjectTaskIdGeneratorStub()),
            clock=ClockStub(now),
        )
        groups = ProjectGroupQueriesStub()
        usecase = AssignProjectTaskUsecase(
            create_task_usecase=create_usecase,
            current_user=CurrentUserStub(current_user_id.value),
            project_queries=ProjectQueriesStub(project),
            project_group_queries=groups,
        )

        with pytest.raises(AccessDeniedError):
            await usecase(
                CreateProjectTaskRequest.from_primitives(
                    project_id=project.id_,
                    title="Prepare KPI",
                    description="Build weekly KPI summary",
                    start_at=now,
                    end_at=now.replace(hour=12),
                    assignees=[ProjectTaskRoleAssignee(ProjectRole.MEMBER)],
                )
            )

    asyncio.run(scenario())


def test_assign_user_denies_target_outside_project() -> None:
    async def scenario() -> None:
        now = datetime(2026, 4, 26, 10, 0, 0)
        current_user_id = UserId("550e8400-e29b-41d4-a716-446655440040")
        target_user_id = UserId("550e8400-e29b-41d4-a716-446655440099")
        project = SimpleNamespace(
            id_="550e8400-e29b-41d4-a716-446655440042",
            members={
                current_user_id: ProjectRole.LEAD,
            },
        )
        create_usecase = CreateProjectTaskUsecase(
            current_user=CurrentUserStub(current_user_id.value),
            project_queries=ProjectQueriesStub(project),
            task_commands=TaskCommandsStub(),
            task_service=ProjectTaskDomainService(ProjectTaskIdGeneratorStub()),
            clock=ClockStub(now),
        )
        usecase = AssignProjectTaskUsecase(
            create_task_usecase=create_usecase,
            current_user=CurrentUserStub(current_user_id.value),
            project_queries=ProjectQueriesStub(project),
            project_group_queries=ProjectGroupQueriesStub(),
        )

        with pytest.raises(AccessDeniedError):
            await usecase(
                CreateProjectTaskRequest.from_primitives(
                    project_id=project.id_,
                    title="Prepare KPI",
                    description="Build weekly KPI summary",
                    start_at=now,
                    end_at=now.replace(hour=12),
                    assignees=[ProjectTaskUserAssignee(target_user_id.value)],
                )
            )

    asyncio.run(scenario())


def test_assign_group_denies_non_member_subject() -> None:
    async def scenario() -> None:
        now = datetime(2026, 4, 26, 10, 0, 0)
        current_user_id = UserId("550e8400-e29b-41d4-a716-446655440050")
        project_id = "550e8400-e29b-41d4-a716-446655440051"
        group_id = ProjectGroupId("550e8400-e29b-41d4-a716-446655440052")
        project = SimpleNamespace(
            id_=project_id,
            members={current_user_id: ProjectRole.LEAD},
        )
        create_usecase = CreateProjectTaskUsecase(
            current_user=CurrentUserStub(current_user_id.value),
            project_queries=ProjectQueriesStub(project),
            task_commands=TaskCommandsStub(),
            task_service=ProjectTaskDomainService(ProjectTaskIdGeneratorStub()),
            clock=ClockStub(now),
        )
        groups = ProjectGroupQueriesStub()
        usecase = AssignProjectTaskUsecase(
            create_task_usecase=create_usecase,
            current_user=CurrentUserStub(current_user_id.value),
            project_queries=ProjectQueriesStub(project),
            project_group_queries=groups,
        )

        with pytest.raises(AccessDeniedError):
            await usecase(
                CreateProjectTaskRequest.from_primitives(
                    project_id=project_id,
                    title="Prepare KPI",
                    description="Build weekly KPI summary",
                    start_at=now,
                    end_at=now.replace(hour=12),
                    assignees=[ProjectTaskGroupAssignee(group_id)],
                )
            )

    asyncio.run(scenario())
