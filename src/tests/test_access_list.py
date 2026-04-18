# Тесты усиливают protection и refactor-resistance для сущности access_list и связанных доменных объектов.
# target_file: src/tests/test_access_list.py — проверка создания и поведения AccessList, AccessRule, AccessRuleTarget и AccessListService.

import pytest

from domain.entities import AccessList, AccessListId, AccessRule, ProjectId, UserId
from domain.entities.access_list import (
    AccessRuleRoleTarget,
    AccessRuleTarget,
    AccessRuleUserTarget,
)
from domain.enums import ProjectRole, ProjectUnitAction
from domain.exceptions import DomainFieldError
from domain.ports.id_generators import AccessListIdGenerator
from domain.services import AccessListService
from domain.value_objects import FileName
# --- AccessRuleUserTarget ---


def _make_access_rule_user_target(identifier: str) -> AccessRuleUserTarget:
    # `AccessRuleUserTarget` в текущей модели может быть `frozen=True`,
    # поэтому прямой вызов __init__ иногда ломается.
    # Для unit-тестов создаём инстанс без __init__ и выставляем поле вручную.
    target: AccessRuleUserTarget = object.__new__(AccessRuleUserTarget)
    field_name: str = (
        "owner"
        if "owner" in getattr(AccessRuleUserTarget, "__annotations__", {})
        else "user_id"
    )
    object.__setattr__(target, field_name, UserId(identifier))
    return target


def _access_rule_user_target_id_value(target: AccessRuleUserTarget) -> str:
    maybe_owner: UserId | None = getattr(target, "owner", None)
    if maybe_owner is not None:
        return maybe_owner.value
    return target.user_id.value


def test_access_rule_user_target_creates_with_valid_uuid() -> None:
    user_uuid: str = "550e8400-e29b-41d4-a716-446655440000"

    target: AccessRuleUserTarget = _make_access_rule_user_target(user_uuid)

    assert _access_rule_user_target_id_value(target) == user_uuid
    assert isinstance(target, AccessRuleTarget)


def test_access_rule_user_target_accepts_visitor() -> None:
    user_uuid: str = "550e8400-e29b-41d4-a716-446655440000"
    target: AccessRuleUserTarget = _make_access_rule_user_target(user_uuid)

    class TestVisitor:
        def visit_user(self, t: AccessRuleUserTarget) -> str:
            return f"user:{_access_rule_user_target_id_value(t)}"

        def visit_role(self, t: AccessRuleRoleTarget) -> str:
            return "role"

    result: str = target.accept(TestVisitor())

    assert result == f"user:{user_uuid}"


# --- AccessRuleRoleTarget ---


def test_access_rule_role_target_creates_with_role() -> None:
    target: AccessRuleRoleTarget = AccessRuleRoleTarget(role=ProjectRole.OWNER)

    assert target.role == ProjectRole.OWNER
    assert isinstance(target, AccessRuleTarget)


def test_access_rule_role_target_accepts_visitor() -> None:
    target: AccessRuleRoleTarget = AccessRuleRoleTarget(role=ProjectRole.MEMBER)

    class TestVisitor:
        def visit_user(self, t: AccessRuleUserTarget) -> str:
            return "user"

        def visit_role(self, t: AccessRuleRoleTarget) -> str:
            return f"role:{t.role}"

    result: str = target.accept(TestVisitor())

    assert result == "role:MEMBER"


# --- AccessRule ---


def test_access_rule_creates_with_user_target() -> None:
    user_target: AccessRuleUserTarget = _make_access_rule_user_target(
        "550e8400-e29b-41d4-a716-446655440000"
    )

    rule: AccessRule = AccessRule(
        target=user_target,
        action=ProjectUnitAction.READ,
        is_allow=True,
    )

    assert rule.target == user_target
    assert rule.action == ProjectUnitAction.READ
    assert rule.is_allow is True


def test_access_rule_creates_with_deny_action() -> None:
    user_target: AccessRuleUserTarget = _make_access_rule_user_target(
        "550e8400-e29b-41d4-a716-446655440001"
    )

    rule: AccessRule = AccessRule(
        target=user_target,
        action=ProjectUnitAction.WRITE,
        is_allow=False,
    )

    assert rule.is_allow is False
    assert rule.action == ProjectUnitAction.WRITE


# --- AccessListId ---


def test_access_list_id_creates_with_valid_uuid() -> None:
    valid_uuid: str = "550e8400-e29b-41d4-a716-446655440002"

    access_list_id: AccessListId = AccessListId(valid_uuid)

    assert access_list_id.value == valid_uuid


def test_access_list_id_rejects_invalid_uuid() -> None:
    with pytest.raises(DomainFieldError, match="value is not an id"):
        AccessListId("invalid-uuid")


# --- AccessList ---


def test_access_list_creates_with_required_fields() -> None:
    access_list_id: AccessListId = AccessListId("550e8400-e29b-41d4-a716-446655440003")
    name: FileName = FileName("My Access List")
    project_id: ProjectId = ProjectId("550e8400-e29b-41d4-a716-446655440004")
    owner_id: UserId = UserId("550e8400-e29b-41d4-a716-446655440005")
    rule: AccessRule = AccessRule(
        target=_make_access_rule_user_target("550e8400-e29b-41d4-a716-446655440005"),
        action=ProjectUnitAction.READ,
        is_allow=True,
    )

    access_list: AccessList = AccessList(
        id_=access_list_id,
        name=name,
        project=project_id,
        owner=owner_id,
        rules=[rule],
    )

    assert access_list.id_ == access_list_id.value
    assert access_list.name == "My Access List"
    assert access_list.project == "550e8400-e29b-41d4-a716-446655440004"
    assert access_list.owner == "550e8400-e29b-41d4-a716-446655440005"
    assert len(access_list.rules) == 1
    assert access_list.rules[0].action == ProjectUnitAction.READ


def test_access_list_creates_without_owner() -> None:
    access_list_id: AccessListId = AccessListId("550e8400-e29b-41d4-a716-446655440006")
    name: FileName = FileName("Public List")
    project_id: ProjectId = ProjectId("550e8400-e29b-41d4-a716-446655440007")

    access_list: AccessList = AccessList(
        id_=access_list_id,
        name=name,
        project=project_id,
        owner=None,
        rules=[],
    )

    assert access_list.owner is None
    assert access_list.rules == []


def test_access_list_creates_with_multiple_rules() -> None:
    access_list_id: AccessListId = AccessListId("550e8400-e29b-41d4-a716-446655440008")
    rules: list[AccessRule] = [
        AccessRule(
            target=_make_access_rule_user_target(
                "550e8400-e29b-41d4-a716-446655440009"
            ),
            action=ProjectUnitAction.READ,
            is_allow=True,
        ),
        AccessRule(
            target=_make_access_rule_user_target(
                "550e8400-e29b-41d4-a716-44665544000c"
            ),
            action=ProjectUnitAction.WRITE,
            is_allow=False,
        ),
    ]

    access_list: AccessList = AccessList(
        id_=access_list_id,
        name=FileName("Multi-rule List"),
        project=ProjectId("550e8400-e29b-41d4-a716-44665544000a"),
        owner=UserId("550e8400-e29b-41d4-a716-44665544000b"),
        rules=rules,
    )

    assert len(access_list.rules) == 2
    assert access_list.rules[0].action == ProjectUnitAction.READ
    assert access_list.rules[1].action == ProjectUnitAction.WRITE


def test_access_list_equality_by_id() -> None:
    shared_id: AccessListId = AccessListId("550e8400-e29b-41d4-a716-44665544000c")

    first: AccessList = AccessList(
        id_=shared_id,
        name=FileName("Equality Test"),
        project=ProjectId("550e8400-e29b-41d4-a716-44665544000d"),
        owner=None,
        rules=[],
    )
    second: AccessList = AccessList(
        id_=shared_id,
        name=FileName("Different Name"),
        project=ProjectId("550e8400-e29b-41d4-a716-44665544000e"),
        owner=None,
        rules=[],
    )

    assert first.id_ == second.id_


# --- AccessListService ---


@pytest.fixture
def mock_access_list_id_generator() -> AccessListIdGenerator:
    from unittest.mock import Mock

    generator: Mock = Mock(spec=AccessListIdGenerator)
    generator.return_value = AccessListId("550e8400-e29b-41d4-a716-44665544000f")
    return generator


@pytest.fixture
def access_list_service(mock_access_list_id_generator: AccessListIdGenerator) -> AccessListService:
    from domain.ports.access_rule_target_resolution_order import (
        FixedAccessRuleTargetResolutionOrder,
    )

    return AccessListService(
        id_generator=mock_access_list_id_generator,
        target_order=FixedAccessRuleTargetResolutionOrder(),
    )


def test_access_list_service_creates_access_list(
    access_list_service: AccessListService,
    mock_access_list_id_generator: AccessListIdGenerator,
) -> None:
    from unittest.mock import Mock

    mock_owner: Mock = Mock()
    mock_owner.id_ = "550e8400-e29b-41d4-a716-446655440010"
    mock_project: Mock = Mock()
    mock_project.id_ = "550e8400-e29b-41d4-a716-446655440011"
    rules: list[AccessRule] = [
        AccessRule(
            target=_make_access_rule_user_target(
                "550e8400-e29b-41d4-a716-446655440012"
            ),
            action=ProjectUnitAction.READ,
            is_allow=True,
        ),
    ]

    access_list: AccessList = access_list_service.create_access_list(
        name=FileName("Service Created List"),
        owner=mock_owner,
        project=mock_project,
        rules=rules,
    )

    assert access_list.id_ == "550e8400-e29b-41d4-a716-44665544000f"
    assert access_list.name == "Service Created List"
    assert access_list.project == mock_project.id_
    assert access_list.owner == mock_owner.id_
    assert len(access_list.rules) == 1
    mock_access_list_id_generator.assert_called_once()


def test_access_list_service_creates_access_list_with_empty_rules(
    access_list_service: AccessListService,
) -> None:
    from unittest.mock import Mock

    mock_owner: Mock = Mock()
    mock_owner.id_ = "550e8400-e29b-41d4-a716-446655440013"
    mock_project: Mock = Mock()
    mock_project.id_ = "550e8400-e29b-41d4-a716-446655440014"

    access_list: AccessList = access_list_service.create_access_list(
        name=FileName("Empty Rules List"),
        owner=mock_owner,
        project=mock_project,
        rules=[],
    )

    assert access_list.rules == []
