from collections.abc import Mapping
from dataclasses import dataclass

from domain.entities import User, Project, UserId, AccessList
from domain.entities.project_task import ProjectTask
from domain.entities.project_group import ProjectGroupId
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


@dataclass(frozen=True, kw_only=True)
class ProjectGroupManagmentContext(PermissionContext):
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
            ),
        )

        if not update_permisson.success:
            return update_permisson

        subject_role: ProjectRole | None = context.target_project.members.get(
            UserId(context.subject.id_), None
        )
        if subject_role == ProjectRole.OWNER:
            return AuthorizationResult(True)

        target_list: AccessList = context.target_list
        if not target_list or target_list.owner == context.subject.id_:
            return AuthorizationResult(True)

        return AuthorizationResult(
            False,
            """Subject is not owner of access list or project itself""",
        )


class CanAssignAccessList(CanUpdateProject): ...


class CanChangePrivateness(CanDeleteProject): ...


class CanManageProjectGroup(CanUpdateProject, Permission[ProjectGroupManagmentContext]):
    def is_satisfied_by(
        self, context: ProjectGroupManagmentContext
    ) -> AuthorizationResult:
        return CanUpdateProject.is_satisfied_by(
            self,
            context=ProjectManagmentContext(
                subject=context.subject,
                target=context.target,
            ),
        )


class CanManageProjectTask(CanUpdateProject): ...


@dataclass(frozen=True, kw_only=True)
class ProjectTaskCompleteContext(PermissionContext):
    subject_id: UserId
    subject_role: ProjectRole | None
    task: ProjectTask
    is_assigned: bool


class CanCompleteProjectTask(Permission[ProjectTaskCompleteContext]):
    def is_satisfied_by(self, context: ProjectTaskCompleteContext) -> AuthorizationResult:
        is_creator = context.task.creator_id == context.subject_id
        is_owner = context.subject_role == ProjectRole.OWNER
        if is_creator or is_owner or context.is_assigned:
            return AuthorizationResult(True)
        return AuthorizationResult(
            False,
            "Only task creator, project owner, or assigned can complete task",
        )


@dataclass(frozen=True, kw_only=True)
class ProjectTaskCancelContext(PermissionContext):
    subject_id: UserId
    subject_role: ProjectRole | None
    task: ProjectTask


class CanCancelProjectTask(Permission[ProjectTaskCancelContext]):
    def is_satisfied_by(self, context: ProjectTaskCancelContext) -> AuthorizationResult:
        is_creator = context.task.creator_id == context.subject_id
        is_owner = context.subject_role == ProjectRole.OWNER
        if is_creator or is_owner:
            return AuthorizationResult(True)
        return AuthorizationResult(
            False,
            "Only task creator or project owner can cancel task",
        )


@dataclass(frozen=True, kw_only=True)
class ProjectGroupParticipantManagmentContext(PermissionContext):
    subject: User
    project: Project
    target: User


class CanAddGroupParticipant(
    CanUpdateProject, Permission[ProjectGroupParticipantManagmentContext]
):
    def __init__(
        self,
        role_hierarchy: Mapping[ProjectRole, set[ProjectRole]] = SUBORDINATE_ROLES,
    ) -> None:
        self._role_hierarchy = role_hierarchy

    def is_satisfied_by(
        self, context: ProjectGroupParticipantManagmentContext
    ) -> AuthorizationResult:

        update_permisson: AuthorizationResult = CanUpdateProject.is_satisfied_by(
            self,
            context=ProjectManagmentContext(
                subject=context.subject, target=context.project
            ),
        )

        if not update_permisson.success:
            return update_permisson

        subject_role: ProjectRole = context.project.members.get(
            UserId(context.subject.id_), None
        )
        target_role: ProjectRole = context.project.members.get(
            UserId(context.target.id_), None
        )

        if target_role is None:
            return AuthorizationResult(
                False,
                detail="Target user is not a project member",
            )

        if subject_role in self._role_hierarchy[target_role]:
            return AuthorizationResult(
                False,
                detail="Subject don't have permissions to add target user, because he higher in role hierarchy",
            )

        return AuthorizationResult(True)


@dataclass(frozen=True, kw_only=True)
class ProjectTaskTeamAssignmentContext(PermissionContext):
    subject: User
    project: Project
    target_group_id: ProjectGroupId
    subject_group_ids: frozenset[ProjectGroupId]
    object_user_id: UserId
    object_group_ids: frozenset[ProjectGroupId]


class CanAssignProjectTaskTeam(Permission[ProjectTaskTeamAssignmentContext]):
    def is_satisfied_by(
        self, context: ProjectTaskTeamAssignmentContext
    ) -> AuthorizationResult:
        subject_role = context.project.members.get(UserId(context.subject.id_))
        is_owner = subject_role == ProjectRole.OWNER
        is_object_user = UserId(context.subject.id_) == context.object_user_id
        is_subject_in_target = context.target_group_id in context.subject_group_ids
        is_object_in_target = context.target_group_id in context.object_group_ids
        if is_owner or is_object_user or (is_subject_in_target and is_object_in_target):
            return AuthorizationResult(True)
        return AuthorizationResult(
            False,
            "Team assignment allowed only for owner, object user, or common team membership",
        )
