from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace

from domain.ports.id_generators import AccessListIdGenerator
from domain.ports.access_rule_responsible_resolution_order import (
    AccessRuleResponsibleResolutionOrder,
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
    AccessRuleResponsibleVisitor,
    ResolvedUnitPermissions,
    AccessRuleResponsible,
    AccessRuleGroupResponsible,
    AccessRuleRoleResponsible,
    AccessRuleUserResponsible,
)


class OwnerResponsibleDetectionVisitor(AccessRuleResponsibleVisitor):
    def __init__(
        self,
        project: Project,
        group_owners_roles: dict[ProjectGroupId, ProjectRole],
    ):
        self._project = project
        self._group_owners_roles = group_owners_roles

    def visit_user(self, responsible: AccessRuleUserResponsible) -> bool:
        return self._project.members.get(responsible.user_id, None) == ProjectRole.OWNER

    def visit_role(self, responsible: AccessRuleRoleResponsible) -> bool:
        return responsible.role == ProjectRole.OWNER

    def visit_group(self, responsible: AccessRuleGroupResponsible) -> bool:
        return self._group_owners_roles.get(responsible.group_id, None) == ProjectRole.OWNER


class AccessRuleResponsibleAppliesVisitor(AccessRuleResponsibleVisitor):
    def __init__(
        self,
        project: Project,
        user_id: UserId,
        user_project_group_ids: frozenset[ProjectGroupId],
    ):
        self._project = project
        self._user_id = user_id
        self._user_project_group_ids = user_project_group_ids

    def visit_user(self, responsible: AccessRuleUserResponsible) -> bool:
        return responsible.user_id == self._user_id

    def visit_role(self, responsible: AccessRuleRoleResponsible) -> bool:
        return self._project.members.get(self._user_id, None) == responsible.role

    def visit_group(self, responsible: AccessRuleGroupResponsible) -> bool:
        return responsible.group_id in self._user_project_group_ids


class AccessListService:
    def __init__(
        self,
        id_generator: AccessListIdGenerator,
        responsible_order: AccessRuleResponsibleResolutionOrder,
    ):
        self._id_generator = id_generator
        self._responsible_order = responsible_order

    def _sort_rules_by_responsible_resolution_order(
        self,
        access_lists: Sequence[AccessList],
        order: AccessRuleResponsibleResolutionOrder,
    ) -> list[AccessList]:
        order_index = {kind: i for i, kind in enumerate(order)}

        def rule_sort_index(rule: AccessRule) -> tuple[int, int]:
            responsible_type: type[AccessRuleResponsible] = type(rule.responsible)
            try:
                return (order_index[responsible_type], rule.order)
            except KeyError as err:
                raise TypeError(
                    f"Unsupported access rule responsible: {responsible_type!r}"
                ) from err

        return [
            replace(
                acl,
                rules=sorted(acl.rules, key=rule_sort_index),
            )
            for acl in access_lists
        ]

    def _sort_and_assign_rule_order(
        self,
        rules: list[AccessRule],
        order: AccessRuleResponsibleResolutionOrder,
    ) -> list[AccessRule]:
        order_index = {kind: i for i, kind in enumerate(order)}

        def responsible_priority(rule: AccessRule) -> int:
            responsible_type: type[AccessRuleResponsible] = type(rule.responsible)
            try:
                return order_index[responsible_type]
            except KeyError as err:
                raise TypeError(
                    f"Unsupported access rule responsible: {responsible_type!r}"
                ) from err

        sorted_rules = sorted(rules, key=responsible_priority)

        result: list[AccessRule] = []
        previous_responsible_type: type[AccessRuleResponsible] | None = None
        responsible_order = 0

        for rule in sorted_rules:
            current_responsible_type = type(rule.responsible)
            if current_responsible_type != previous_responsible_type:
                responsible_order = 0
            else:
                responsible_order += 1

            result.append(replace(rule, order=responsible_order))
            previous_responsible_type = current_responsible_type

        return result

    def create_access_list(
        self,
        name: FileName,
        owner: User,
        project: Project,
        rules: list[AccessRule],
        group_owners_roles: dict[ProjectGroupId, ProjectRole] | None = None,
    ) -> AccessList:
        group_owners_roles = group_owners_roles or {}
        rules = self._sort_and_assign_rule_order(rules, self._responsible_order)

        responsibles: set[AccessRule] = set()

        for rule in rules:
            if self.responsible_is_owner(rule, project, group_owners_roles):
                raise OwnerInAccessListError(
                    "Access list cannot reference owner responsible, "
                    "because owner must have full control on project"
                )

            if rule in responsibles:
                raise AccessRuleMismatchError(
                    "Access list cannot have multiple rule for same responsible and action"
                )

            responsibles.add(rule)

        return AccessList(
            id_=self._id_generator(),
            name=name,
            owner=UserId(owner.id_),
            project=ProjectId(project.id_),
            rules=rules,
        )

    def responsible_is_owner(
        self,
        rule: AccessRule,
        project: Project,
        group_owners_roles: dict[ProjectGroupId, ProjectRole],
    ) -> bool:
        visitor = OwnerResponsibleDetectionVisitor(project, group_owners_roles)
        return rule.responsible.accept(visitor)

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

        lists = self._sort_rules_by_responsible_resolution_order(
            access_lists, self._responsible_order
        )
        resolved = ResolvedUnitPermissions()
        applies_visitor = AccessRuleResponsibleAppliesVisitor(
            project, user_id, user_project_group_ids
        )

        for access_list in lists:
            for rule in access_list.rules:
                if not rule.responsible.accept(applies_visitor):
                    continue

                if rule.is_allow and rule.action not in resolved.denied:
                    resolved.allowed.add(rule.action)
                if not rule.is_allow:
                    if rule.action not in resolved.allowed:
                        resolved.denied.add(rule.action)
        return resolved
