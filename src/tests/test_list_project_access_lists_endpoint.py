# Тест усиливает protection и refactor-resistance для contract endpoint’а списка ACL по проекту.
# target_file: src/tests/test_list_project_access_lists_endpoint.py — проверка GET `/project/{project_id}/acl` и схемы ответа.

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import cast
from uuid import UUID

from fastapi import APIRouter, FastAPI
from fastapi.routing import APIRoute
from pydantic import UUID4
from starlette.requests import Request as StarletteRequest

from domain.enums import ProjectUnitAction
from presentation.http.controllers.projects.list_access_lists import (
    create_list_acls_router,
)
from presentation.models import AccessListRead
from presentation.models.access_list import UserAccessRule


class StubListProjectAccessListsHandler:
    def __init__(
        self,
        *,
        expected_project_id: UUID4,
        expected_offset: int,
        expected_limit: int,
        expected_filter_name: str,
        expected_orders: str,
        expected_access_list_id: UUID4,
        expected_created_by: UUID4,
        expected_owner_name: str,
        expected_acl_name: str,
        expected_rule_responsible: str,
        expected_rule_action: ProjectUnitAction,
    ) -> None:
        self._expected_project_id: UUID4 = expected_project_id
        self._expected_offset: int = expected_offset
        self._expected_limit: int = expected_limit
        self._expected_filter_name: str = expected_filter_name
        self._expected_orders: str = expected_orders

        self._expected_access_list_id: UUID4 = expected_access_list_id
        self._expected_created_by: UUID4 = expected_created_by
        self._expected_owner_name: str = expected_owner_name
        self._expected_acl_name: str = expected_acl_name

        self._expected_rule_responsible: str = expected_rule_responsible
        self._expected_rule_action: ProjectUnitAction = expected_rule_action

    async def __call__(
        self,
        *,
        raw_filters: dict[str, str],
        project_id: UUID4,
        raw_orders: str,
        offset: int,
        limit: int,
    ) -> list[AccessListRead]:
        assert project_id == self._expected_project_id
        assert offset == self._expected_offset
        assert limit == self._expected_limit
        assert raw_orders == self._expected_orders

        assert raw_filters == {"name": self._expected_filter_name}

        return [
            AccessListRead(
                id_=self._expected_access_list_id,
                created_by=self._expected_created_by,
                owner_name=self._expected_owner_name,
                name=self._expected_acl_name,
                rules=[
                    UserAccessRule(
                        responsible=UUID(self._expected_rule_responsible),
                        display_name="User (550e84)",
                        action=self._expected_rule_action,
                        type="ALLOW",
                    )
                ],
            )
        ]


class StubAsyncDishkaContainer:
    def __init__(self, handler: StubListProjectAccessListsHandler) -> None:
        self._handler: StubListProjectAccessListsHandler = handler

    def __call__(
        self, additional_context: object, scope: object | None = None
    ) -> "StubAsyncDishkaContainer":
        return self

    async def __aenter__(self) -> "StubAsyncDishkaContainer":
        return self

    async def __aexit__(
        self, exc_type: object, exc: object, tb: object
    ) -> None:
        return None

    async def get(
        self, type_hint: object, component: object | None = None
    ) -> StubListProjectAccessListsHandler:
        return self._handler


def test_list_project_acl_endpoint_delegates_to_handler_and_returns_response() -> None:
    expected_project_id_str: str = "550e8400-e29b-41d4-a716-446655440000"
    expected_offset: int = 5
    expected_limit: int = 2
    expected_filter_name: str = "My ACL"
    expected_orders: str = '[{"field":"name","direction":"asc"}]'

    expected_access_list_id_str: str = "550e8400-e29b-41d4-a716-44665544000f"
    expected_created_by_str: str = "550e8400-e29b-41d4-a716-446655440010"
    expected_owner_name: str = "Owner Name"
    expected_acl_name: str = "ACL #1"
    expected_rule_responsible: str = "550e8400-e29b-41d4-a716-446655440020"
    expected_rule_action: ProjectUnitAction = ProjectUnitAction.READ

    expected_project_id: UUID4 = UUID(expected_project_id_str)  # type: ignore[assignment]
    expected_access_list_id: UUID4 = UUID(expected_access_list_id_str)  # type: ignore[assignment]
    expected_created_by: UUID4 = UUID(expected_created_by_str)  # type: ignore[assignment]

    stub_handler: StubListProjectAccessListsHandler = StubListProjectAccessListsHandler(
        expected_project_id=expected_project_id,
        expected_offset=expected_offset,
        expected_limit=expected_limit,
        expected_filter_name=expected_filter_name,
        expected_orders=expected_orders,
        expected_access_list_id=expected_access_list_id,
        expected_created_by=expected_created_by,
        expected_owner_name=expected_owner_name,
        expected_acl_name=expected_acl_name,
        expected_rule_responsible=expected_rule_responsible,
        expected_rule_action=expected_rule_action,
    )

    app: FastAPI = FastAPI()
    projects_router: APIRouter = APIRouter(prefix="/project", tags=["project"])
    projects_router.include_router(create_list_acls_router())
    app.include_router(projects_router)

    route = next(
        r
        for r in app.routes
        if isinstance(r, APIRoute)
        and r.path == "/project/{project_id}/acl"
        and "GET" in r.methods
    )
    endpoint = cast(object, route.endpoint)

    raw_endpoint = getattr(endpoint, "__wrapped__", endpoint)
    endpoint_callable: Callable[..., Awaitable[list[AccessListRead]]] = cast(
        Callable[..., Awaitable[list[AccessListRead]]], raw_endpoint
    )

    stub_container: StubAsyncDishkaContainer = StubAsyncDishkaContainer(stub_handler)

    async def receive() -> dict[str, object]:
        return {
            "type": "http.request",
            "body": b"",
            "more_body": False,
        }

    dishka_request: StarletteRequest = StarletteRequest(
        scope={"type": "http", "method": "GET", "path": "/"},
        receive=receive,
    )
    dishka_request.state.dishka_container = stub_container

    result: list[AccessListRead] = asyncio.run(
        endpoint_callable(
            project_id=expected_project_id,
            offset=expected_offset,
            limit=expected_limit,
            name=expected_filter_name,
            orders=expected_orders,
            ___dishka_request=dishka_request,
        )
    )

    assert len(result) == 1
    assert result[0].id_ == expected_access_list_id
    assert result[0].created_by == expected_created_by
    assert result[0].owner_name == expected_owner_name
    assert result[0].name == expected_acl_name
    assert str(result[0].rules[0].responsible) == expected_rule_responsible
    assert result[0].rules[0].action == expected_rule_action
    assert result[0].rules[0].type == "ALLOW"

