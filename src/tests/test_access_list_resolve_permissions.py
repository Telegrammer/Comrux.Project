from datetime import UTC, datetime
from unittest.mock import Mock

from domain.entities import (
    AccessList,
    AccessListId,
    AccessRule,
    Project,
    ProjectId,
    UserId,
)
from domain.entities.access_list import AccessRuleGroupTarget, AccessRuleRoleTarget
from domain.entities.project_group import ProjectGroupId
from domain.enums import ProjectRole, ProjectUnitAction
from domain.ports.access_rule_target_resolution_order import (
    FixedAccessRuleTargetResolutionOrder,
)
from domain.services import AccessListService
from domain.value_objects import FileName, PassedDatetime, Title


def _make_access_list(
    *,
    list_id: str,
    project_id: str,
    owner_id: str,
    rules: list[AccessRule],
) -> AccessList:
    return AccessList(
        id_=AccessListId(list_id),
        name=FileName("ACL"),
        project=ProjectId(project_id),
        owner=UserId(owner_id),
        rules=rules,
    )


def _secure_rule(is_allow: bool) -> AccessRule:
    return AccessRule(
        target=AccessRuleRoleTarget(role=ProjectRole.MEMBER),
        action=ProjectUnitAction.SECURE,
        is_allow=is_allow,
    )


def _member_project(project_id: str, member_user_id: str) -> Project:
    now = datetime.now(UTC)
    return Project(
        id_=ProjectId(project_id),
        title=Title("test-project"),
        root_directory=None,
        created_at=PassedDatetime(now, now),
        members={UserId(member_user_id): ProjectRole.MEMBER},
    )


def test_resolve_permissions_returns_empty_sets_when_no_rules() -> None:
    service = AccessListService(
        id_generator=Mock(),
        target_order=FixedAccessRuleTargetResolutionOrder(),
    )
    project_id = "550e8400-e29b-41d4-a716-446655440100"
    actor = "550e8400-e29b-41d4-a716-446655440101"
    project = _member_project(project_id, actor)

    resolved = service.resolve_permissions([], project, UserId(actor))

    assert resolved.allowed == set()
    assert resolved.denied == set()


def test_resolve_permissions_prefers_child_rule_over_parent() -> None:
    service = AccessListService(
        id_generator=Mock(),
        target_order=FixedAccessRuleTargetResolutionOrder(),
    )
    project_id = "550e8400-e29b-41d4-a716-446655440111"
    actor = "550e8400-e29b-41d4-a716-446655440116"
    project = _member_project(project_id, actor)

    child_acl = _make_access_list(
        list_id="550e8400-e29b-41d4-a716-446655440112",
        project_id=project_id,
        owner_id="550e8400-e29b-41d4-a716-446655440113",
        rules=[_secure_rule(is_allow=False)],
    )
    parent_acl = _make_access_list(
        list_id="550e8400-e29b-41d4-a716-446655440114",
        project_id=project_id,
        owner_id="550e8400-e29b-41d4-a716-446655440115",
        rules=[_secure_rule(is_allow=True)],
    )

    resolved = service.resolve_permissions([child_acl, parent_acl], project, UserId(actor))

    assert ProjectUnitAction.SECURE in resolved.denied
    assert ProjectUnitAction.SECURE not in resolved.allowed


def test_resolve_permissions_uses_parent_when_child_has_no_secure_rule() -> None:
    service = AccessListService(
        id_generator=Mock(),
        target_order=FixedAccessRuleTargetResolutionOrder(),
    )
    project_id = "550e8400-e29b-41d4-a716-446655440121"
    actor = "550e8400-e29b-41d4-a716-446655440126"
    project = _member_project(project_id, actor)

    child_acl = _make_access_list(
        list_id="550e8400-e29b-41d4-a716-446655440122",
        project_id=project_id,
        owner_id="550e8400-e29b-41d4-a716-446655440123",
        rules=[],
    )
    parent_acl = _make_access_list(
        list_id="550e8400-e29b-41d4-a716-446655440124",
        project_id=project_id,
        owner_id="550e8400-e29b-41d4-a716-446655440125",
        rules=[_secure_rule(is_allow=True)],
    )

    resolved = service.resolve_permissions([child_acl, parent_acl], project, UserId(actor))

    assert ProjectUnitAction.SECURE in resolved.allowed
    assert ProjectUnitAction.SECURE not in resolved.denied

