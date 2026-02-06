from collections.abc import Mapping
from dataclasses import dataclass

from domain.entities import User, Project, ProjectId, UserId
from domain.enums.project_roles import ProjectRole
from .base import Permission, PermissionContext, AuthorizationResult
from .role_hierarchy import (
    SUBORDINATE_ROLES,
)


@dataclass(frozen=True, kw_only=True)
class UserManagementContext(PermissionContext):
    subject: User
    target: User


class CanManageSelf(Permission[UserManagementContext]):
    def is_satisfied_by(self, context: UserManagementContext) -> AuthorizationResult:
        if context.subject == context.target:
            return AuthorizationResult(True)
        return AuthorizationResult(False, "Subject and target users are not the same")


@dataclass(frozen=True, kw_only=True)
class ProjectManagmentContext(PermissionContext):
    subject: User
    target: Project


class CanDeleteProject(Permission[ProjectManagmentContext]):
    def is_satisfied_by(self, context: ProjectManagmentContext) -> bool:
        subject_id: UserId = context.subject.id_
        subject_role: ProjectRole = context.target.members.get(UserId(subject_id), None)
        if subject_role == ProjectRole.OWNER:
            return AuthorizationResult(True)
        return AuthorizationResult(False, "Project can be deleted only by owner")


class CanUpdateProject(Permission[ProjectManagmentContext]):

    def is_satisfied_by(self, context: ProjectManagmentContext) -> bool:
        subject_id: UserId = context.subject.id_
        subject_role: ProjectRole = context.target.members.get(UserId(subject_id), None)
        if subject_role == ProjectRole.OWNER:
            return AuthorizationResult(True)
        return AuthorizationResult(
            False, "Project meta can't be updated by members/guests"
        )


@dataclass(frozen=True, kw_only=True)
class RoleManagementContext(PermissionContext):
    subject_role: ProjectRole
    target_role: ProjectRole


class CanManageRole(Permission[RoleManagementContext]):
    def __init__(
        self,
        role_hierarchy: Mapping[ProjectRole, set[ProjectRole]] = SUBORDINATE_ROLES,
    ) -> None:
        self._role_hierarchy = role_hierarchy

    def is_satisfied_by(self, context: RoleManagementContext) -> bool:
        allowed_roles = self._role_hierarchy.get(context.subject_role, set())
        if context.target_role in allowed_roles:
            return AuthorizationResult(True)
        return AuthorizationResult(
            False,
            f"""Subject's role ({context.subject_role}) don't allow
            to manage target role ({context.target_role})""",
        )
