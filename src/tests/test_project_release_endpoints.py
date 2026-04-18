# Этот тест усиливает protection и refactor-resistance для HTTP-контрактов project release.
# target_file: src/tests/test_project_release_endpoints.py — проверка create, status и download endpoint’ов релиза.

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
from starlette.responses import Response

from application.export.contracts import ProjectReleaseDownload
from presentation.export import (
    ProjectReleaseCreate,
    ProjectReleaseCreatedResponse,
    ProjectReleaseReadResponse,
    ProjectReleasesListResponse,
)
from presentation.http.controllers.projects.releases import create_project_release_router


class StubAsyncDishkaContainer:
    def __init__(self, handler: object) -> None:
        self._handler = handler

    def __call__(
        self,
        additional_context: object,
        scope: object | None = None,
    ) -> "StubAsyncDishkaContainer":
        del additional_context
        del scope
        return self

    async def __aenter__(self) -> "StubAsyncDishkaContainer":
        return self

    async def __aexit__(
        self,
        exc_type: object,
        exc: object,
        tb: object,
    ) -> None:
        del exc_type
        del exc
        del tb

    async def get(self, type_hint: object, component: object | None = None) -> object:
        del type_hint
        del component
        return self._handler


class StubCreateProjectReleaseHandler:
    async def __call__(
        self,
        project_id: UUID4,
        request: ProjectReleaseCreate,
    ) -> ProjectReleaseCreatedResponse:
        assert request.name == "release-1"
        return ProjectReleaseCreatedResponse(
            release_id="550e8400-e29b-41d4-a716-446655440010",
            project_id=str(project_id),
            status="CREATED",
            name=request.name,
        )


class StubGetProjectReleaseHandler:
    async def __call__(
        self, project_id: UUID4, release_id: UUID4
    ) -> ProjectReleaseReadResponse:
        return ProjectReleaseReadResponse(
            id_=str(release_id),
            project_id=str(project_id),
            name="release-1",
            status="READY",
            file_name="release-1.zip",
            archive_size=256,
            error_message=None,
            created_at="2026-04-14T12:00:00+00:00",
            started_at="2026-04-14T12:01:00+00:00",
            finished_at="2026-04-14T12:02:00+00:00",
        )


class StubDownloadProjectReleaseHandler:
    async def __call__(
        self,
        project_id: UUID4,
        release_id: UUID4,
    ) -> ProjectReleaseDownload:
        del project_id
        del release_id
        return ProjectReleaseDownload(
            file_name="release-1.zip",
            media_type="application/zip",
            content=b"zip-content",
        )


class StubListProjectReleasesHandler:
    async def __call__(
        self,
        project_id: UUID4,
        limit: int,
        offset: int,
    ) -> ProjectReleasesListResponse:
        assert limit == 20
        assert offset == 0
        return ProjectReleasesListResponse(
            items=[
                ProjectReleaseReadResponse(
                    id_="550e8400-e29b-41d4-a716-446655440010",
                    project_id=str(project_id),
                    name="release-1",
                    status="READY",
                    file_name="release-1.zip",
                    archive_size=256,
                    error_message=None,
                    created_at="2026-04-14T12:00:00+00:00",
                    started_at="2026-04-14T12:01:00+00:00",
                    finished_at="2026-04-14T12:02:00+00:00",
                )
            ],
            total=1,
        )


def _dishka_request(handler: object, method: str) -> StarletteRequest:
    async def receive() -> dict[str, object]:
        return {
            "type": "http.request",
            "body": b"",
            "more_body": False,
        }

    request = StarletteRequest(
        scope={"type": "http", "method": method, "path": "/"},
        receive=receive,
    )
    request.state.dishka_container = StubAsyncDishkaContainer(handler)
    return request


def _route(app: FastAPI, path: str, method: str) -> APIRoute:
    return next(
        route
        for route in app.routes
        if isinstance(route, APIRoute) and route.path == path and method in route.methods
    )


def test_list_project_releases_endpoint_returns_list_payload() -> None:
    project_id: UUID4 = UUID("550e8400-e29b-41d4-a716-446655440001")  # type: ignore[assignment]
    app = FastAPI()
    projects_router = APIRouter(prefix="/project", tags=["project"])
    projects_router.include_router(create_project_release_router())
    app.include_router(projects_router)
    route = _route(app, "/project/{project_id}/releases", "GET")
    endpoint = cast(
        Callable[..., Awaitable[ProjectReleasesListResponse]],
        getattr(route.endpoint, "__wrapped__", route.endpoint),
    )

    result = asyncio.run(
        endpoint(
            project_id=project_id,
            limit=20,
            offset=0,
            token=HTTPAuthorizationCredentials(scheme="Bearer", credentials="token"),
            ___dishka_request=_dishka_request(StubListProjectReleasesHandler(), "GET"),
        )
    )

    assert result.total == 1
    assert result.items[0].status == "READY"
    assert result.items[0].name == "release-1"


def test_create_project_release_endpoint_returns_created_payload() -> None:
    project_id: UUID4 = UUID("550e8400-e29b-41d4-a716-446655440001")  # type: ignore[assignment]
    app = FastAPI()
    projects_router = APIRouter(prefix="/project", tags=["project"])
    projects_router.include_router(create_project_release_router())
    app.include_router(projects_router)
    route = _route(app, "/project/{project_id}/releases", "POST")
    endpoint = cast(
        Callable[..., Awaitable[ProjectReleaseCreatedResponse]],
        getattr(route.endpoint, "__wrapped__", route.endpoint),
    )

    result = asyncio.run(
        endpoint(
            project_id=project_id,
            request_body=ProjectReleaseCreate(name="release-1"),
            token=HTTPAuthorizationCredentials(scheme="Bearer", credentials="token"),
            ___dishka_request=_dishka_request(StubCreateProjectReleaseHandler(), "POST"),
        )
    )

    assert result.status == "CREATED"
    assert result.name == "release-1"


def test_get_project_release_endpoint_returns_status_payload() -> None:
    project_id: UUID4 = UUID("550e8400-e29b-41d4-a716-446655440001")  # type: ignore[assignment]
    release_id: UUID4 = UUID("550e8400-e29b-41d4-a716-446655440010")  # type: ignore[assignment]
    app = FastAPI()
    projects_router = APIRouter(prefix="/project", tags=["project"])
    projects_router.include_router(create_project_release_router())
    app.include_router(projects_router)
    route = _route(app, "/project/{project_id}/releases/{release_id}", "GET")
    endpoint = cast(
        Callable[..., Awaitable[ProjectReleaseReadResponse]],
        getattr(route.endpoint, "__wrapped__", route.endpoint),
    )

    result = asyncio.run(
        endpoint(
            project_id=project_id,
            release_id=release_id,
            token=HTTPAuthorizationCredentials(scheme="Bearer", credentials="token"),
            ___dishka_request=_dishka_request(StubGetProjectReleaseHandler(), "GET"),
        )
    )

    assert result.status == "READY"
    assert result.file_name == "release-1.zip"


def test_download_project_release_endpoint_returns_zip_response() -> None:
    project_id: UUID4 = UUID("550e8400-e29b-41d4-a716-446655440001")  # type: ignore[assignment]
    release_id: UUID4 = UUID("550e8400-e29b-41d4-a716-446655440010")  # type: ignore[assignment]
    app = FastAPI()
    projects_router = APIRouter(prefix="/project", tags=["project"])
    projects_router.include_router(create_project_release_router())
    app.include_router(projects_router)
    route = _route(app, "/project/{project_id}/releases/{release_id}/download", "GET")
    endpoint = cast(
        Callable[..., Awaitable[Response]],
        getattr(route.endpoint, "__wrapped__", route.endpoint),
    )

    result = asyncio.run(
        endpoint(
            project_id=project_id,
            release_id=release_id,
            token=HTTPAuthorizationCredentials(scheme="Bearer", credentials="token"),
            ___dishka_request=_dishka_request(StubDownloadProjectReleaseHandler(), "GET"),
        )
    )

    assert result.body == b"zip-content"
    assert result.headers["content-type"] == "application/zip"
    assert "release-1.zip" in result.headers["content-disposition"]
