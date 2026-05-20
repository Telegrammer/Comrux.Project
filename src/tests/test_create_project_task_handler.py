import asyncio
from datetime import datetime

from domain.entities import ProjectId
from presentation.handlers import CreateProjectTaskHandler
from presentation.models import (
    ProjectTaskAssigneeGroupPayload,
    ProjectTaskAssigneeRolePayload,
    ProjectTaskAssigneeUserPayload,
    ProjectTaskCreate,
)


class CompositionStub:
    def __init__(self) -> None:
        self.called = False
        self.captured_assignees = []

    async def __call__(self, request):
        self.called = True
        self.captured_assignees = request.assignees
        return {
            "task_id": "550e8400-e29b-41d4-a716-446655440060",
            "project_id": ProjectId("550e8400-e29b-41d4-a716-446655440061"),
        }


class AssigneePresenterStub:
    def to_domain_assignee(self, target):
        return target


def test_create_task_handler_accepts_mixed_assignee_kinds() -> None:
    async def scenario() -> None:
        composition = CompositionStub()
        handler = CreateProjectTaskHandler(
            composition=composition,
            assignee_presenter=AssigneePresenterStub(),
        )

        response = await handler(
            "550e8400-e29b-41d4-a716-446655440062",  # type: ignore[arg-type]
            ProjectTaskCreate(
                title="Prepare roadmap",
                description="Roadmap",
                start_at=datetime(2026, 4, 26, 10, 0, 0),
                end_at=datetime(2026, 4, 26, 11, 0, 0),
                assignees=[
                    ProjectTaskAssigneeUserPayload(
                        user_id="550e8400-e29b-41d4-a716-446655440063"
                    ),
                    ProjectTaskAssigneeRolePayload(role="MEMBER"),
                    ProjectTaskAssigneeGroupPayload(
                        group_id="550e8400-e29b-41d4-a716-446655440064"
                    ),
                ],
            ),
        )

        assert composition.called is True
        assert [assignee.kind for assignee in composition.captured_assignees] == [
            "user",
            "role",
            "group",
        ]
        assert str(response.task_id) == "550e8400-e29b-41d4-a716-446655440060"

    asyncio.run(scenario())
