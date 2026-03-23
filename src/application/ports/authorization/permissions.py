from collections.abc import Mapping
from dataclasses import dataclass

from domain.entities import User, Project, ProjectId, UserId, AccessList
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
    def is_satisfied_by(self, context: ProjectManagmentContext) -> AuthorizationResult:
        subject_id: UserId = context.subject.id_
        subject_role: ProjectRole = context.target.members.get(UserId(subject_id), None)
        if subject_role == ProjectRole.OWNER:
            return AuthorizationResult(True)
        return AuthorizationResult(False, "Project can be deleted only by owner")


class CanUpdateProject(Permission[ProjectManagmentContext]):

    def is_satisfied_by(self, context: ProjectManagmentContext) -> AuthorizationResult:
        subject_id: UserId = context.subject.id_
        subject_role: ProjectRole = context.target.members.get(UserId(subject_id), None)
        if subject_role not in {ProjectRole.OWNER, ProjectRole.LEAD}:
            return AuthorizationResult(
                False, "Project meta can't be updated by members/guests"
            )

        return AuthorizationResult(True)


@dataclass(frozen=True, kw_only=True)
class ProjectContentManagmentContext(PermissionContext):
    subject: User
    target: Project


class CanManageProjectContent(Permission[ProjectManagmentContext]):

    def is_satisfied_by(self, context):
        if UserId(context.subject.id_) not in context.target.members.keys():
            return AuthorizationResult(
                False, "Only members of the project can manage it"
            )
        return AuthorizationResult(True)


@dataclass(frozen=True, kw_only=True)
class RoleManagementContext(PermissionContext):
    subject_role: ProjectRole
    target_role: ProjectRole
    new_role: ProjectRole


class CanManageRole(Permission[RoleManagementContext]):
    def __init__(
        self,
        role_hierarchy: Mapping[ProjectRole, set[ProjectRole]] = SUBORDINATE_ROLES,
    ) -> None:
        self._role_hierarchy = role_hierarchy

    def is_satisfied_by(self, context: RoleManagementContext) -> AuthorizationResult:
        allowed_roles = self._role_hierarchy.get(context.subject_role, set())

        if context.target_role not in allowed_roles:
            return AuthorizationResult(
                False,
                f"""Subject's role ({context.subject_role}) don't allow
                to manage target role ({context.target_role})""",
            )

        if context.new_role not in allowed_roles:
            return AuthorizationResult(
                False,
                f"""Current role ({context.subject_role}) don't allow
                to set higher role ({context.new_role}) then self""",
            )

        return AuthorizationResult(True)


@dataclass(frozen=True, kw_only=True)
class AccessListManagmentContext(PermissionContext):
    subject: User
    target_project: Project
    target_list: AccessList


class CanDeleteAccessList(CanUpdateProject, Permission[AccessListManagmentContext]):

    def is_satisfied_by(
        self, context: AccessListManagmentContext
    ) -> AuthorizationResult:

        update_permisson: AuthorizationResult = CanUpdateProject.is_satisfied_by(
            self,
            context=ProjectManagmentContext(
                subject=context.subject, target=context.target_project
            )
        )

        if not update_permisson.success:
            return update_permisson

        subject_role: ProjectRole | None = context.target_project.members.get(
            context.subject.id_, None
        )
        if subject_role == ProjectRole.OWNER:
            return AuthorizationResult(True)

        target_list: AccessList = context.target_list
        if not target_list or target_list.owner == context.subject.id_:
            return AuthorizationResult(True)

        return AuthorizationResult(
            False,
            f"""Subject is not owner of access list or project itself""",
        )
