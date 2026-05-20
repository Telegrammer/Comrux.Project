import asyncio
from dataclasses import dataclass
from types import SimpleNamespace

from application.ports.gateways.query_params import (
    EqFilter,
    InFilter,
    LikeFilter,
    OffsetPagination,
    ProjectTaskListParams,
    SortingOrder,
    SortingParam,
)
from application.usecases import ListProjectTasksRequest, ListProjectTasksUsecase
from domain.entities import ProjectId, UserId
from domain.enums import ProjectRole
from presentation.handlers import ListProjectTasksHandler


class OrdersPresenterStub:
    def __call__(self, _raw_orders: str):
        return []


class TimeOrdersPresenterStub:
    def __call__(self, _raw_orders: str):
        return [SortingParam("created_at", SortingOrder.DESCENDING)]


class ListTasksCompositionStub:
    def __init__(self) -> None:
        self.captured_params: ProjectTaskListParams | None = None

    async def __call__(self, _request, params: ProjectTaskListParams):
        self.captured_params = params
        return []


def test_list_tasks_handler_adds_active_filter() -> None:
    async def scenario() -> None:
        composition = ListTasksCompositionStub()
        handler = ListProjectTasksHandler(
            usecase=composition,
            orders_presenter=OrdersPresenterStub(),
        )

        await handler(
            project_id="550e8400-e29b-41d4-a716-446655440201",  # type: ignore[arg-type]
            raw_orders="[]",
            offset=0,
            limit=10,
            scope="active",
        )

        assert composition.captured_params is not None
        assert any(
            isinstance(f, InFilter)
            and f.field_name == "status"
            and f.values == ["PLANNED", "IN_PROGRESS"]
            for f in composition.captured_params.filters
        )

    asyncio.run(scenario())


def test_list_tasks_handler_sets_mine_flag_for_mine_scope() -> None:
    async def scenario() -> None:
        composition = ListTasksCompositionStub()
        handler = ListProjectTasksHandler(
            usecase=composition,
            orders_presenter=OrdersPresenterStub(),
        )

        await handler(
            project_id="550e8400-e29b-41d4-a716-446655440202",  # type: ignore[arg-type]
            raw_orders="[]",
            offset=0,
            limit=10,
            scope="mine",
        )

        assert composition.captured_params is not None
        assert composition.captured_params.mine is True

    asyncio.run(scenario())


def test_list_tasks_handler_adds_name_filter() -> None:
    async def scenario() -> None:
        composition = ListTasksCompositionStub()
        handler = ListProjectTasksHandler(
            usecase=composition,
            orders_presenter=OrdersPresenterStub(),
        )

        await handler(
            project_id="550e8400-e29b-41d4-a716-446655440205",  # type: ignore[arg-type]
            raw_orders="[]",
            offset=0,
            limit=10,
            name="feature",
        )

        assert composition.captured_params is not None
        assert any(
            isinstance(f, LikeFilter)
            and f.field_name == "title"
            and f.value == "feature"
            for f in composition.captured_params.filters
        )

    asyncio.run(scenario())


def test_list_tasks_handler_passes_time_sorting() -> None:
    async def scenario() -> None:
        composition = ListTasksCompositionStub()
        handler = ListProjectTasksHandler(
            usecase=composition,
            orders_presenter=TimeOrdersPresenterStub(),
        )

        await handler(
            project_id="550e8400-e29b-41d4-a716-446655440206",  # type: ignore[arg-type]
            raw_orders='[{"created_at":"DESC"}]',
            offset=0,
            limit=10,
        )

        assert composition.captured_params is not None
        assert composition.captured_params.sorting == [
            SortingParam("created_at", SortingOrder.DESCENDING)
        ]

    asyncio.run(scenario())


class ClockStub:
    def now(self):
        return "2026-04-28T00:00:00"


class CurrentUserStub:
    def __init__(self, user_id: str) -> None:
        self._user = SimpleNamespace(id_=user_id)

    async def __call__(self):
        return self._user


class ProjectQueriesStub:
    def __init__(self, project_id: str, user_id: UserId) -> None:
        self._project = SimpleNamespace(
            id_=project_id,
            members={user_id: ProjectRole.MEMBER},
        )

    async def by_id(self, _project_id: str):
        return self._project


class TaskCommandsStub:
    async def sync_overdue_batch(self, _project_id: ProjectId, _now):
        return 0


@dataclass
class TaskQueriesStub:
    captured_params: ProjectTaskListParams | None = None

    async def by_project(self, _project_id: ProjectId, params: ProjectTaskListParams):
        self.captured_params = params
        return []


def test_list_tasks_usecase_resolves_mine_flag_to_assigned_user() -> None:
    async def scenario() -> None:
        user_id = UserId("550e8400-e29b-41d4-a716-446655440203")
        task_queries = TaskQueriesStub()
        usecase = ListProjectTasksUsecase(
            clock=ClockStub(),
            current_user=CurrentUserStub(user_id.value),
            project_queries=ProjectQueriesStub(
                project_id="550e8400-e29b-41d4-a716-446655440204",
                user_id=user_id,
            ),
            task_commands=TaskCommandsStub(),
            task_queries=task_queries,
        )

        await usecase(
            ListProjectTasksRequest.from_primitives(
                "550e8400-e29b-41d4-a716-446655440204"
            ),
            ProjectTaskListParams(
                filters=[],
                pagination=OffsetPagination(0, 10),
                sorting=[],
                mine=True,
            ),
        )

        assert task_queries.captured_params is not None
        assert task_queries.captured_params.assigned_to_user_id == user_id.value
        assert task_queries.captured_params.mine is False

    asyncio.run(scenario())
