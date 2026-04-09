from domain.ports.id_generators import AccessListIdGenerator
from domain.value_objects import FileName
from domain.enums import ProjectRole
from domain.exceptions import OwnerInAccessListError, AccessRuleMismatchError
from domain.entities import (
    Project,
    User,
    AccessRule,
    AccessList,
    UserId,
    ProjectId,
)
from domain.entities.access_list import (
    AccessRuleTargetVisitor,
    ResolvedUnitPermissions,
    AccessRuleRoleTarget,
    AccessRuleUserTarget,
)


class OwnerTargetDetectionVisitor(AccessRuleTargetVisitor):
    def __init__(self, project: Project):
        self._project = project

    def visit_user(self, target: AccessRuleUserTarget) -> bool:
        return self._project.members.get(target.user_id, None) == ProjectRole.OWNER

    def visit_role(self, target: AccessRuleRoleTarget) -> bool:
        return target.role == ProjectRole.OWNER


class AccessRuleTargetAppliesVisitor(AccessRuleTargetVisitor):
    def __init__(self, project: Project, user_id: UserId):
        self._project = project
        self._user_id = user_id

    def visit_user(self, target: AccessRuleUserTarget) -> bool:
        return target.user_id == self._user_id

    def visit_role(self, target: AccessRuleRoleTarget) -> bool:
        return self._project.members.get(self._user_id, None) == target.role


class AccessListService:
    def __init__(self, id_generator: AccessListIdGenerator):
        self._id_generator = id_generator

    def create_access_list(
        self, name: FileName, owner: User, project: Project, rules: list[AccessRule]
    ) -> AccessList:

        targets: set[AccessRule] = set()

        for rule in rules:
            if self.targets_owner(rule, project):
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

    def targets_owner(self, rule: AccessRule, project: Project) -> bool:
        visitor = OwnerTargetDetectionVisitor(project)
        return rule.target.accept(visitor)

    def belongs_to(self, access_list: AccessList, project: Project) -> bool:
        return access_list.project == project.id_

    def resolve_permissions(
        self,
        sorted_lists: list[AccessList],
        project: Project,
        user_id: UserId,
    ) -> ResolvedUnitPermissions:
        resolved = ResolvedUnitPermissions()
        applies_visitor = AccessRuleTargetAppliesVisitor(project, user_id)

        for access_list in sorted_lists:
            for rule in access_list.rules:
                if not rule.target.accept(applies_visitor):
                    continue

                if rule.is_allow and rule.action not in resolved.denied:
                    resolved.allowed.add(rule.action)
                if not rule.is_allow and rule.action not in resolved.allowed:
                    resolved.denied.add(rule.action)

        return resolved
