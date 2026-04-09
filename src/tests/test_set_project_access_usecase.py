import asyncio
from datetime import datetime, timezone
from typing import Optional
from unittest.mock import Mock

import pytest

from application.exceptions import AccessDeniedError, ProjectNotFoundError
from application.usecases.set_project_access import (
    SetProjectAccessRequest,
    SetProjectAccessUsecase,
)
from domain.entities import Project, ProjectId, User, UserId
from domain.enums import ProjectRole
from domain.services import ProjectService
from domain.value_objects import Name, PassedDatetime, Title


class FakeClock:
    def __init__(self, now: datetime) -> None:
        self._now: datetime = now

    def now(self) -> datetime:
        return self._now


class FakeProjectQueries:
    def __init__(
        self,
        *,
        project: Optional[Project],
        exc: Optional[Exception],
    ) -> None:
        self._project: Optional[Project] = project
        self._exc: Optional[Exception] = exc
        self.received_project_id: Optional[str] = None

    async def by_id(self, project_id: str) -> Project:
        self.received_project_id = project_id
        if self._exc is not None:
            raise self._exc
        if self._project is None:
            raise ProjectNotFoundError("Project not found")
        return self._project


class FakeProjectCommands:
    def __init__(self) -> None:
        self.updated_projects: list[Project] = []

    async def update(self, project: Project) -> None:
        self.updated_projects.append(project)


class FakeCurrentUserService:
    def __init__(self, user: User) -> None:
        self._user: User = user
        self.called: bool = False

    async def __call__(self) -> User:
        self.called = True
        return self._user


def _build_owner_project(*, project_uuid: str, owner_uuid: str) -> Project:
    now: datetime = datetime(2026, 3, 26, tzinfo=timezone.utc)
    return Project(
        id_=ProjectId(project_uuid),
        title=Title("TestProject"),
        root_directory=None,
        description="",
        members={UserId(owner_uuid): ProjectRole.OWNER},
        created_at=PassedDatetime(now, now),
    )


def _build_user(*, user_uuid: str, name: str) -> User:
    return User(
        id_=UserId(user_uuid),
        name=Name(name),
        bio="",
    )


def test_set_project_access_updates_is_private_when_authorized() -> None:
    # protection + refactor-resistance: фиксируем контракт смены privateness у OWNER.

    project_uuid: str = "550e8400-e29b-41d4-a716-446655440001"
    owner_uuid: str = "550e8400-e29b-41d4-a716-446655440010"
    now: datetime = datetime(2026, 3, 26, tzinfo=timezone.utc)

    project: Project = _build_owner_project(
        project_uuid=project_uuid, owner_uuid=owner_uuid
    )
    current_user: User = _build_user(user_uuid=owner_uuid, name="Owner")

    clock: FakeClock = FakeClock(now=now)
    project_queries: FakeProjectQueries = FakeProjectQueries(
        project=project, exc=None
    )
    project_commands: FakeProjectCommands = FakeProjectCommands()
    current_user_service: FakeCurrentUserService = FakeCurrentUserService(
        user=current_user
    )

    project_service: ProjectService = ProjectService(id_generator=Mock())

    usecase: SetProjectAccessUsecase = SetProjectAccessUsecase(
        clock=clock,
        project_service=project_service,
        project_queries=project_queries,
        project_commands=project_commands,
        current_user=current_user_service,
    )

    request: SetProjectAccessRequest = SetProjectAccessRequest(
        project_id=ProjectId(project_uuid),
        is_private=True,
    )

    asyncio.run(usecase(request))

    assert project_queries.received_project_id == request.project_id.value
    assert current_user_service.called is True
    assert len(project_commands.updated_projects) == 1
    assert project_commands.updated_projects[0] is project
    assert project.is_private is True


def test_set_project_access_raises_when_current_user_is_not_owner() -> None:
    # protection: запрещаем изменение privateness не-OWNER.

    project_uuid: str = "550e8400-e29b-41d4-a716-446655440002"
    owner_uuid: str = "550e8400-e29b-41d4-a716-446655440011"
    not_owner_uuid: str = "550e8400-e29b-41d4-a716-446655440012"

    project: Project = _build_owner_project(
        project_uuid=project_uuid, owner_uuid=owner_uuid
    )
    current_user: User = _build_user(
        user_uuid=not_owner_uuid, name="NotOwner"
    )

    clock: FakeClock = FakeClock(now=datetime.now(tz=timezone.utc))
    project_queries: FakeProjectQueries = FakeProjectQueries(
        project=project, exc=None
    )
    project_commands: FakeProjectCommands = FakeProjectCommands()
    current_user_service: FakeCurrentUserService = FakeCurrentUserService(
        user=current_user
    )

    project_service: ProjectService = ProjectService(id_generator=Mock())

    usecase: SetProjectAccessUsecase = SetProjectAccessUsecase(
        clock=clock,
        project_service=project_service,
        project_queries=project_queries,
        project_commands=project_commands,
        current_user=current_user_service,
    )

    request: SetProjectAccessRequest = SetProjectAccessRequest(
        project_id=ProjectId(project_uuid),
        is_private=True,
    )

    with pytest.raises(AccessDeniedError):
        asyncio.run(usecase(request))

    assert current_user_service.called is True
    assert project_commands.updated_projects == []
    assert project.is_private is False


def test_set_project_access_propagates_project_not_found_error() -> None:
    # fast feedback + protection: если проекта нет — не трогаем команды/текущего пользователя.

    project_uuid: str = "550e8400-e29b-41d4-a716-446655440003"
    owner_uuid: str = "550e8400-e29b-41d4-a716-446655440013"
    now: datetime = datetime(2026, 3, 26, tzinfo=timezone.utc)

    current_user: User = _build_user(user_uuid=owner_uuid, name="Owner")
    clock: FakeClock = FakeClock(now=now)
    project_queries: FakeProjectQueries = FakeProjectQueries(
        project=None,
        exc=ProjectNotFoundError("Project not found"),
    )
    project_commands: FakeProjectCommands = FakeProjectCommands()
    current_user_service: FakeCurrentUserService = FakeCurrentUserService(
        user=current_user
    )

    project_service: ProjectService = ProjectService(id_generator=Mock())

    usecase: SetProjectAccessUsecase = SetProjectAccessUsecase(
        clock=clock,
        project_service=project_service,
        project_queries=project_queries,
        project_commands=project_commands,
        current_user=current_user_service,
    )

    request: SetProjectAccessRequest = SetProjectAccessRequest(
        project_id=ProjectId(project_uuid),
        is_private=True,
    )

    with pytest.raises(ProjectNotFoundError):
        asyncio.run(usecase(request))

    assert project_queries.received_project_id == request.project_id.value
    assert current_user_service.called is False
    assert project_commands.updated_projects == []

