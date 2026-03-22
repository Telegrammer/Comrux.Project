# Тест усиливает protection и refactor-resistance для контрактного endpoint’а создания ACL по проекту.
# target_file: src/tests/test_create_access_list_endpoint.py — проверка POST `/project/{project_id}/acl` и схемы ответа.

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import cast
from uuid import UUID

from fastapi import APIRouter, FastAPI
from fastapi.routing import APIRoute
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import UUID4
from starlette.requests import Request as StarletteRequest

from domain.enums import ProjectUnitAction
from presentation.http.controllers.projects.add_access_list import create_add_acl_router
from presentation.models import AccessListCreated
from presentation.models.access_list import AccessListCreate, AccessRule


class StubCreateAccessListHandler:
    def __init__(
        self,
        *,
        expected_project_id: UUID4,
        expected_name: str,
        expected_rule_target: str,
        expected_rule_action: ProjectUnitAction,
        expected_access_list_id: UUID4,
        expected_created_by: UUID4,
    ) -> None:
        self._expected_project_id: UUID4 = expected_project_id
        self._expected_name: str = expected_name
        self._expected_rule_target: str = expected_rule_target
        self._expected_rule_action: ProjectUnitAction = expected_rule_action
        self._expected_access_list_id: UUID4 = expected_access_list_id
        self._expected_created_by: UUID4 = expected_created_by

    async def __call__(
        self,
        request: AccessListCreate,
        project_id: UUID4,
    ) -> AccessListCreated:
        # Контракт контроллера: handler вызывается как `handler(project_id, request_body)`.
        assert project_id == self._expected_project_id
        assert request.name == self._expected_name
        assert len(request.rules) == 1
        rule = request.rules[0]
        assert rule.target == self._expected_rule_target
        assert rule.action == self._expected_rule_action
        assert rule.type == "ALLOW"

        return AccessListCreated(
            id_=self._expected_access_list_id,
            created_by=self._expected_created_by,
        )


class StubAsyncDishkaContainer:
    def __init__(self, handler: StubCreateAccessListHandler) -> None:
        self._handler: StubCreateAccessListHandler = handler

    def __call__(
        self, additional_context: object, scope: object | None = None
    ) -> "StubAsyncDishkaContainer":
        # В dishka создаётся "контекстный" child container; для теста это не нужно.
        return self

    async def __aenter__(self) -> "StubAsyncDishkaContainer":
        return self

    async def __aexit__(
        self, exc_type: object, exc: object, tb: object
    ) -> None:
        return None

    async def get(
        self, type_hint: object, component: object | None = None
    ) -> StubCreateAccessListHandler:
        # В endpoint’е dependency соответствует FromDishka[CreateAccessListHandler].
        return self._handler


def test_create_access_list_endpoint_delegates_to_handler_and_returns_response() -> None:
    expected_project_id_str: str = "550e8400-e29b-41d4-a716-446655440000"
    expected_access_list_id_str: str = "550e8400-e29b-41d4-a716-44665544000f"
    expected_created_by_str: str = "550e8400-e29b-41d4-a716-446655440010"
    expected_rule_target: str = "550e8400-e29b-41d4-a716-446655440020"
    expected_name: str = "Test ACL"
    expected_rule_action: ProjectUnitAction = ProjectUnitAction.READ

    expected_project_id: UUID4 = UUID(expected_project_id_str)  # type: ignore[assignment]
    expected_access_list_id: UUID4 = UUID(expected_access_list_id_str)  # type: ignore[assignment]
    expected_created_by: UUID4 = UUID(expected_created_by_str)  # type: ignore[assignment]

    stub_handler: StubCreateAccessListHandler = StubCreateAccessListHandler(
        expected_project_id=expected_project_id,
        expected_name=expected_name,
        expected_rule_target=expected_rule_target,
        expected_rule_action=expected_rule_action,
        expected_access_list_id=expected_access_list_id,
        expected_created_by=expected_created_by,
    )
    app: FastAPI = FastAPI()
    projects_router: APIRouter = APIRouter(prefix="/project", tags=["project"])
    projects_router.include_router(create_add_acl_router())
    app.include_router(projects_router)

    route = next(
        r
        for r in app.routes
        if isinstance(r, APIRoute)
        and r.path == "/project/{project_id}/acl"
        and "POST" in r.methods
    )
    endpoint = cast(object, route.endpoint)

    # dishka `@inject` может оборачивать endpoint; если есть __wrapped__, берём оригинал.
    raw_endpoint = getattr(endpoint, "__wrapped__", endpoint)

    request_body: AccessListCreate = AccessListCreate(
        name=expected_name,
        rules=[
            AccessRule(
                target=expected_rule_target,
                action=expected_rule_action,
                type="ALLOW",
            ),
        ],
    )
    token: HTTPAuthorizationCredentials = HTTPAuthorizationCredentials(
        scheme="Bearer", credentials="test-token"
    )

    endpoint_callable: Callable[..., Awaitable[AccessListCreated]] = cast(
        Callable[..., Awaitable[AccessListCreated]], raw_endpoint
    )

    stub_container: StubAsyncDishkaContainer = StubAsyncDishkaContainer(stub_handler)

    async def receive() -> dict[str, object]:
        return {
            "type": "http.request",
            "body": b"",
            "more_body": False,
        }

    dishka_request: StarletteRequest = StarletteRequest(
        scope={"type": "http", "method": "POST", "path": "/"},
        receive=receive,
    )
    dishka_request.state.dishka_container = stub_container

    result: AccessListCreated = asyncio.run(
        endpoint_callable(
            project_id=expected_project_id,
            request_body=request_body,
            token=token,
            ___dishka_request=dishka_request,
        )
    )

    assert result.id_ == expected_access_list_id
    assert result.created_by == expected_created_by

