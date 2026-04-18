from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace

from domain.ports.id_generators import AccessListIdGenerator
from domain.ports.access_rule_target_resolution_order import (
    AccessRuleTargetResolutionOrder,
)
from domain.value_objects import FileName
from domain.enums import ProjectRole, ProjectUnitAction
from domain.exceptions import OwnerInAccessListError, AccessRuleMismatchError
from domain.entities import (
    Project,
    User,
    AccessRule,
    AccessList,
    UserId,
    ProjectId,
)
from domain.entities.project_group import ProjectGroupId
from domain.entities.access_list import (
    AccessRuleTargetVisitor,
    ResolvedUnitPermissions,
    AccessRuleTarget,
    AccessRuleGroupTarget,
    AccessRuleRoleTarget,
    AccessRuleUserTarget,
)


class OwnerTargetDetectionVisitor(AccessRuleTargetVisitor):
    def __init__(
        self,
        project: Project,
        group_owners_roles: dict[ProjectGroupId, ProjectRole],
    ):
        self._project = project
        self._group_owners_roles = group_owners_roles

    def visit_user(self, target: AccessRuleUserTarget) -> bool:
        return self._project.members.get(target.user_id, None) == ProjectRole.OWNER

    def visit_role(self, target: AccessRuleRoleTarget) -> bool:
        return target.role == ProjectRole.OWNER

    def visit_group(self, target: AccessRuleGroupTarget) -> bool:
        return self._group_owners_roles.get(target.group_id, None) == ProjectRole.OWNER


class AccessRuleTargetAppliesVisitor(AccessRuleTargetVisitor):
    def __init__(
        self,
        project: Project,
        user_id: UserId,
        user_project_group_ids: frozenset[ProjectGroupId],
    ):
        self._project = project
        self._user_id = user_id
        self._user_project_group_ids = user_project_group_ids

    def visit_user(self, target: AccessRuleUserTarget) -> bool:
        return target.user_id == self._user_id

    def visit_role(self, target: AccessRuleRoleTarget) -> bool:
        return self._project.members.get(self._user_id, None) == target.role

    def visit_group(self, target: AccessRuleGroupTarget) -> bool:
        return target.group_id in self._user_project_group_ids


class AccessListService:
    def __init__(
        self,
        id_generator: AccessListIdGenerator,
        target_order: AccessRuleTargetResolutionOrder,
    ):
        self._id_generator = id_generator
        self._target_order = target_order

    def _sort_rules_by_target_resolution_order(
        self,
        access_lists: Sequence[AccessList],
        order: AccessRuleTargetResolutionOrder,
    ) -> list[AccessList]:
        order_index = {kind: i for i, kind in enumerate(order)}

        def rule_sort_index(rule: AccessRule) -> int:
            target_type: type[AccessRuleTarget] = type(rule.target)
            try:
                return order_index[target_type]
            except KeyError as err:
                raise TypeError(
                    f"Unsupported access rule target: {target_type!r}"
                ) from err

        return [
            replace(
                acl,
                rules=sorted(acl.rules, key=rule_sort_index),
            )
            for acl in access_lists
        ]

    def create_access_list(
        self,
        name: FileName,
        owner: User,
        project: Project,
        rules: list[AccessRule],
        group_owners_roles: dict[ProjectGroupId, ProjectRole] | None = None,
    ) -> AccessList:
        group_owners_roles = group_owners_roles or {}

        targets: set[AccessRule] = set()

        for rule in rules:
            if self.targets_owner(rule, project, group_owners_roles):
                raise OwnerInAccessListError(
                    "Access list cannot target to owner, "
                    "because owner must have full control on project"
                )

            if rule in targets:
                raise AccessRuleMismatchError(
                    "Access list cannot have multiple rule for same target and action"
                )

            targets.add(rule)

        return AccessList(
            id_=self._id_generator(),
            name=name,
            owner=UserId(owner.id_),
            project=ProjectId(project.id_),
            rules=rules,
        )

    def targets_owner(
        self,
        rule: AccessRule,
        project: Project,
        group_owners_roles: dict[ProjectGroupId, ProjectRole],
    ) -> bool:
        visitor = OwnerTargetDetectionVisitor(project, group_owners_roles)
        return rule.target.accept(visitor)

    def belongs_to(self, access_list: AccessList, project: Project) -> bool:
        return access_list.project == project.id_

    def resolve_permissions(
        self,
        access_lists: Sequence[AccessList],
        project: Project,
        user_id: UserId,
        *,
        user_project_group_ids: frozenset[ProjectGroupId] = frozenset(),
    ) -> ResolvedUnitPermissions:
        if project.members.get(user_id) == ProjectRole.OWNER:
            return ResolvedUnitPermissions(
                allowed=set(ProjectUnitAction),
                denied=set(),
            )

        lists = self._sort_rules_by_target_resolution_order(
            access_lists, self._target_order
        )
        resolved = ResolvedUnitPermissions()
        applies_visitor = AccessRuleTargetAppliesVisitor(
            project, user_id, user_project_group_ids
        )

        for access_list in lists:
            for rule in access_list.rules:
                if not rule.target.accept(applies_visitor):
                    continue
                print(resolved)

                if rule.is_allow and rule.action not in resolved.denied:
                    resolved.allowed.add(rule.action)
                if not rule.is_allow:
                    print(
                        rule.action,
                        resolved.allowed,
                        rule.action not in resolved.allowed,
                    )
                    if rule.action not in resolved.allowed:
                        resolved.denied.add(rule.action)
                        print("added")
        print(resolved)

        return resolved
