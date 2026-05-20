import asyncio
from datetime import datetime
from types import SimpleNamespace

import pytest

from application.exceptions import AccessDeniedError
from application.models import ProjectTaskDetailsRead, ProjectTaskGroupAssigneeRead
from application.usecases import (
    GetProjectTaskRequest,
    GetProjectTaskResponse,
    GetProjectTaskUsecase,
)
from domain.entities import (
    ProjectGroupId,
    ProjectId,
    ProjectTask,
    ProjectTaskId,
    UserId,
)
from domain.enums import ProjectRole, ProjectTaskStatus
from domain.value_objects import EmailAddress, Name
from presentation.handlers import GetProjectTaskHandler


class ClockStub:
    def __init__(self, current_time: datetime) -> None:
        self._current_time = current_time

    def now(self) -> datetime:
        return self._current_time


class CurrentUserStub:
    def __init__(self, user_id: UserId) -> None:
        self._user = SimpleNamespace(id_=user_id.value)

    async def __call__(self) -> SimpleNamespace:
        return self._user


class ProjectQueryGatewayStub:
    def __init__(self, project_id: ProjectId, member_id: UserId | None) -> None:
        members = {member_id: ProjectRole.MEMBER} if member_id is not None else {}
        self._project = SimpleNamespace(id_=project_id.value, members=members)

    async def by_id(self, project_id: str) -> SimpleNamespace:
        return self._project


class ProjectTaskCommandGatewayStub:
    def __init__(self) -> None:
        self.synced_project_id: str | None = None

    async def sync_overdue_batch(self, project_id: str, _now: datetime) -> int:
        self.synced_project_id = project_id
        return 0


class ProjectTaskQueryGatewayStub:
    def __init__(self, task_details: ProjectTaskDetailsRead) -> None:
        self._task_details = task_details
        self.details_requested = False

    async def by_id_detailed(self, _task_id: ProjectTaskId) -> ProjectTaskDetailsRead:
        self.details_requested = True
        return self._task_details

    async def by_id(self, _task_id: ProjectTaskId) -> ProjectTask:
        return self._task_details.task


class UserQueryGatewayStub:
    def __init__(self, email: EmailAddress, name: Name) -> None:
        self._user = SimpleNamespace(email=email, name=name)

    async def by_id(self, _user_id: str) -> SimpleNamespace:
        return self._user


class GetProjectTaskCompositionStub:
    def __init__(self, response: GetProjectTaskResponse) -> None:
        self._response = response

    async def __call__(self, _request: GetProjectTaskRequest) -> GetProjectTaskResponse:
        return self._response


def _task(project_id: ProjectId, creator_id: UserId) -> ProjectTask:
    current_time = datetime(2026, 4, 28, 10, 0, 0)
    return ProjectTask(
        id_=ProjectTaskId("550e8400-e29b-41d4-a716-446655440301"),
        project_id=project_id,
        title="Prepare roadmap",
        description="Draft project roadmap",
        status=ProjectTaskStatus.IN_PROGRESS,
        creator_id=creator_id,
        start_at=current_time,
        end_at=current_time.replace(hour=12),
        created_at=current_time,
        updated_at=current_time,
        assignees=[],
    )


def _task_details(project_id: ProjectId, creator_id: UserId) -> ProjectTaskDetailsRead:
    user_id = UserId("550e8400-e29b-41d4-a716-446655440303")
    group_id = ProjectGroupId("550e8400-e29b-41d4-a716-446655440304")
    return ProjectTaskDetailsRead(
        task=_task(project_id, creator_id),
        role_assignees={ProjectRole.MEMBER},
        user_assignees={user_id: Name("Assigned User")},
        group_assignees={
            group_id: ProjectTaskGroupAssigneeRead(
                name=Name("Product Team"),
                color="#ffcc00",
            )
        },
    )


def test_get_project_task_usecase_returns_task_details_with_creator() -> None:
    async def scenario() -> None:
        project_id = ProjectId("550e8400-e29b-41d4-a716-446655440302")
        current_user_id = UserId("550e8400-e29b-41d4-a716-446655440305")
        creator_id = UserId("550e8400-e29b-41d4-a716-446655440306")
        task_commands = ProjectTaskCommandGatewayStub()
        task_queries = ProjectTaskQueryGatewayStub(_task_details(project_id, creator_id))
        usecase = GetProjectTaskUsecase(
            clock=ClockStub(datetime(2026, 4, 28, 10, 0, 0)),
            task_commands=task_commands,
            task_queries=task_queries,
            current_user=CurrentUserStub(current_user_id),
            project_gateway=ProjectQueryGatewayStub(project_id, current_user_id),
            user_gateway=UserQueryGatewayStub(
                EmailAddress("creator@example.com"), Name("Task Creator")
            ),
        )

        response = await usecase(
            GetProjectTaskRequest.from_primitives(
                project_id.value, "550e8400-e29b-41d4-a716-446655440301"
            )
        )

        assert response["id_"] == "550e8400-e29b-41d4-a716-446655440301"
        assert response["project_id"] == project_id.value
        assert response["creator_id"] == creator_id.value
        assert response["creator_email"].value == "creator@example.com"
        assert response["creator_name"].value == "Task Creator"
        assert response["role_assignees"] == {ProjectRole.MEMBER}
        assert len(response["user_assignees"]) == 1
        assert len(response["group_assignees"]) == 1
        assert task_commands.synced_project_id == project_id.value
        assert task_queries.details_requested is True

    asyncio.run(scenario())


def test_get_project_task_usecase_denies_non_member_before_task_lookup() -> None:
    async def scenario() -> None:
        project_id = ProjectId("550e8400-e29b-41d4-a716-446655440307")
        current_user_id = UserId("550e8400-e29b-41d4-a716-446655440308")
        creator_id = UserId("550e8400-e29b-41d4-a716-446655440309")
        task_queries = ProjectTaskQueryGatewayStub(_task_details(project_id, creator_id))
        usecase = GetProjectTaskUsecase(
            clock=ClockStub(datetime(2026, 4, 28, 10, 0, 0)),
            task_commands=ProjectTaskCommandGatewayStub(),
            task_queries=task_queries,
            current_user=CurrentUserStub(current_user_id),
            project_gateway=ProjectQueryGatewayStub(project_id, None),
            user_gateway=UserQueryGatewayStub(
                EmailAddress("creator@example.com"), Name("Task Creator")
            ),
        )

        with pytest.raises(AccessDeniedError):
            await usecase(
                GetProjectTaskRequest.from_primitives(
                    project_id.value, "550e8400-e29b-41d4-a716-446655440301"
                )
            )

        assert task_queries.details_requested is False

    asyncio.run(scenario())


def test_get_project_task_handler_formats_assignees_for_presentation() -> None:
    async def scenario() -> None:
        current_time = datetime(2026, 4, 28, 10, 0, 0)
        project_id = "550e8400-e29b-41d4-a716-446655440310"
        task_id = ProjectTaskId("550e8400-e29b-41d4-a716-446655440311")
        creator_id = "550e8400-e29b-41d4-a716-446655440312"
        user_id = UserId("550e8400-e29b-41d4-a716-446655440313")
        group_id = ProjectGroupId("550e8400-e29b-41d4-a716-446655440314")
        handler = GetProjectTaskHandler(
            GetProjectTaskCompositionStub(
                {
                    "id_": task_id.value,
                    "project_id": project_id,
                    "creator_id": creator_id,
                    "creator_email": EmailAddress("creator@example.com"),
                    "creator_name": Name("Task Creator"),
                    "title": "Prepare roadmap",
                    "description": "Draft project roadmap",
                    "status": ProjectTaskStatus.IN_PROGRESS,
                    "start_at": current_time,
                    "end_at": current_time.replace(hour=12),
                    "created_at": current_time,
                    "updated_at": current_time,
                    "role_assignees": {ProjectRole.MEMBER},
                    "user_assignees": {user_id: Name("Assigned User")},
                    "group_assignees": {
                        group_id: ProjectTaskGroupAssigneeRead(
                            name=Name("Product Team"),
                            color="#ffcc00",
                        )
                    },
                }
            )
        )

        response = await handler(project_id, task_id.value)  # type: ignore[arg-type]

        assert str(response.id_) == task_id.value
        assert str(response.project_id) == project_id
        assert str(response.creator_id) == creator_id
        assert response.creator_email == "creator@example.com"
        assert response.creator_name == "Task Creator"
        assert response.title == "Prepare roadmap"
        assert [assignee.kind for assignee in response.assignees] == [
            "role",
            "user",
            "group",
        ]
        assert [assignee.name for assignee in response.assignees] == [
            ProjectRole.MEMBER.value,
            "Assigned User",
            "Product Team",
        ]
        assert response.assignees[2].color == "#ffcc00"

    asyncio.run(scenario())
