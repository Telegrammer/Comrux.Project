# Тесты SECURE-политики AssignAccessListService.

import asyncio
from dataclasses import dataclass
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from application.exceptions import AccessListNotInProjectError
from application.exceptions.authorization import AccessDeniedError
from application.services import AssignAccessListService


@dataclass
class StubUnit:
    access_list: object | None = None


@dataclass
class StubResolvedPermissions:
    allowed: set[object]
    denied: set[object]


def test_assign_access_list_service_explicit_deny_blocks_even_with_baseline_allow(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    acl_queries = SimpleNamespace(by_id=AsyncMock(name="by_id"))
    unit_permissions = AsyncMock(name="unit_permissions")
    unit_commands = SimpleNamespace(update=AsyncMock(name="update"))
    service = AssignAccessListService(
        acl_queries=acl_queries,
        unit_permissions=unit_permissions,
        unit_commands=unit_commands,
    )

    current_user = SimpleNamespace(id_="user-1")
    project = SimpleNamespace(id_="project-1")
    unit = StubUnit(access_list="old-acl")
    secure_action = SimpleNamespace(name="SECURE")
    unit_permissions.return_value = StubResolvedPermissions(
        allowed=set(),
        denied={secure_action},
    )
    authorize_stub = Mock(name="authorize_stub")
    authorize_stub.return_value = None

    import application.services.access_list_assignment as mod

    monkeypatch.setattr(mod.ProjectUnitAction, "SECURE", secure_action)
    monkeypatch.setattr(mod, "authorize", authorize_stub)

    with pytest.raises(AccessDeniedError):
        asyncio.run(
            service(
                current_user=current_user,
                project=project,
                unit=unit,
                access_list_id=None,
            )
        )
    authorize_stub.assert_not_called()
    unit_commands.update.assert_not_awaited()
    acl_queries.by_id.assert_not_awaited()


def test_assign_access_list_service_explicit_allow_overrides_baseline(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    acl_queries = SimpleNamespace(by_id=AsyncMock(name="by_id"))
    unit_permissions = AsyncMock(name="unit_permissions")
    unit_commands = SimpleNamespace(update=AsyncMock(name="update"))
    service = AssignAccessListService(
        acl_queries=acl_queries,
        unit_permissions=unit_permissions,
        unit_commands=unit_commands,
    )

    current_user = SimpleNamespace(id_="user-1")
    project = SimpleNamespace(id_="project-1")
    unit = StubUnit(access_list="old-acl")
    secure_action = SimpleNamespace(name="SECURE")
    unit_permissions.return_value = StubResolvedPermissions(
        allowed={secure_action},
        denied=set(),
    )
    authorize_stub = Mock(name="authorize_stub")
    # baseline authorize should not be called when explicit allow SECURE exists
    authorize_stub.side_effect = AssertionError("baseline authorize should not run")

    import application.services.access_list_assignment as mod

    monkeypatch.setattr(mod.ProjectUnitAction, "SECURE", secure_action)
    monkeypatch.setattr(mod, "authorize", authorize_stub)

    asyncio.run(
        service(
            current_user=current_user,
            project=project,
            unit=unit,
            access_list_id=None,
        )
    )

    authorize_stub.assert_not_called()
    assert unit.access_list is None
    unit_commands.update.assert_awaited_once_with(unit)
    acl_queries.by_id.assert_not_awaited()


def test_assign_access_list_service_default_deny_uses_baseline_and_denies(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    acl_queries = SimpleNamespace(by_id=AsyncMock(name="by_id"))
    unit_permissions = AsyncMock(name="unit_permissions")
    unit_commands = SimpleNamespace(update=AsyncMock(name="update"))
    service = AssignAccessListService(
        acl_queries=acl_queries,
        unit_permissions=unit_permissions,
        unit_commands=unit_commands,
    )

    current_user = SimpleNamespace(id_="user-1")
    project = SimpleNamespace(id_="project-1")
    unit = StubUnit(access_list="old-acl")
    secure_action = SimpleNamespace(name="SECURE")
    unit_permissions.return_value = StubResolvedPermissions(
        allowed=set(),
        denied=set(),
    )
    authorize_stub = Mock(name="authorize_stub")
    authorize_stub.side_effect = AccessDeniedError("baseline denied")

    import application.services.access_list_assignment as mod
    monkeypatch.setattr(mod.ProjectUnitAction, "SECURE", secure_action)
    monkeypatch.setattr(mod, "authorize", authorize_stub)

    with pytest.raises(AccessDeniedError):
        asyncio.run(
            service(
                current_user=current_user,
                project=project,
                unit=unit,
                access_list_id=None,
            )
        )
    authorize_stub.assert_called_once()
    unit_commands.update.assert_not_awaited()
    acl_queries.by_id.assert_not_awaited()


def test_assign_access_list_service_raises_when_acl_not_in_project(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    acl_queries = SimpleNamespace(by_id=AsyncMock(name="by_id"))
    unit_permissions = AsyncMock(name="unit_permissions")
    unit_commands = SimpleNamespace(update=AsyncMock(name="update"))
    service = AssignAccessListService(
        acl_queries=acl_queries,
        unit_permissions=unit_permissions,
        unit_commands=unit_commands,
    )

    current_user = SimpleNamespace(id_="user-1")
    project = SimpleNamespace(id_="project-1")
    unit = StubUnit(access_list="old-acl")
    secure_action = SimpleNamespace(name="SECURE")
    unit_permissions.return_value = StubResolvedPermissions(
        allowed={secure_action},
        denied=set(),
    )
    access_list = SimpleNamespace(project="other-project", id_="acl-1")
    access_list_id = "acl-id-request"
    acl_queries.by_id.return_value = access_list

    authorize_stub = Mock(name="authorize_stub")
    import application.services.access_list_assignment as mod

    monkeypatch.setattr(mod.ProjectUnitAction, "SECURE", secure_action)
    monkeypatch.setattr(mod, "authorize", authorize_stub)

    with pytest.raises(AccessListNotInProjectError):
        asyncio.run(
            service(
                current_user=current_user,
                project=project,
                unit=unit,
                access_list_id=access_list_id,
            )
        )

    authorize_stub.assert_not_called()
    unit_commands.update.assert_not_awaited()
    acl_queries.by_id.assert_awaited_once_with(access_list_id)

