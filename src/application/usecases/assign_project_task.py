from dataclasses import dataclass

from application.exceptions import AccessDeniedError
from application.ports.authorization import (
    CanAssignProjectTaskTeam,
    CanManageProjectTask,
    CanManageRole,
    ProjectManagmentContext,
    ProjectTaskTeamAssignmentContext,
    RoleManagementContext,
    authorize,
)
from application.ports.gateways import ProjectGroupQueryGateway, ProjectQueryGateway
from application.services import CurrentUserService
from application.usecases.create_project_task import (
    CreateProjectTaskRequest,
    CreateProjectTaskResponse,
    CreateProjectTaskUsecase,
)
from domain.entities import (
    Project,
    ProjectTaskAssigneeVisitor,
    ProjectTaskGroupAssignee,
    ProjectTaskRoleAssignee,
    ProjectTaskUserAssignee,
    User,
    UserId,
)
from domain.enums import ProjectRole


@dataclass
class _ResponsiblePermissionVisitor(ProjectTaskAssigneeVisitor):
    project: Project
    subject: User
    subject_id: UserId
    subject_role: ProjectRole
    subject_group_ids: frozenset

    def visit_user(self, responsible: ProjectTaskUserAssignee) -> None:
        target_role = self.project.members.get(responsible.user_id)
        if target_role is None:
            raise AccessDeniedError("Assignee user does not belong to project")
        authorize(
            CanManageRole(),
            context=RoleManagementContext(
                subject_role=self.subject_role,
                target_role=target_role,
                new_role=target_role,
            ),
        )

    def visit_role(self, responsible: ProjectTaskRoleAssignee) -> None:
        authorize(
            CanManageRole(),
            context=RoleManagementContext(
                subject_role=self.subject_role,
                target_role=responsible.role,
                new_role=responsible.role,
            ),
        )

    def visit_group(self, responsible: ProjectTaskGroupAssignee) -> None:
        if (
            self.subject_role != ProjectRole.OWNER
            and responsible.group_id not in self.subject_group_ids
        ):
            raise AccessDeniedError(
                "Group assignee is allowed only for owner or group member"
            )
        authorize(
            CanAssignProjectTaskTeam(),
            context=ProjectTaskTeamAssignmentContext(
                subject=self.subject,
                project=self.project,
                target_group_id=responsible.group_id,
                subject_group_ids=self.subject_group_ids,
                object_user_id=self.subject_id,
                object_group_ids=self.subject_group_ids,
            ),
        )


class AssignProjectTaskUsecase:
    def __init__(
        self,
        create_task_usecase: CreateProjectTaskUsecase,
        current_user: CurrentUserService,
        project_queries: ProjectQueryGateway,
        project_group_queries: ProjectGroupQueryGateway,
    ) -> None:
        self._create_task_usecase = create_task_usecase
        self._current_user = current_user
        self._project_queries = project_queries
        self._project_group_queries = project_group_queries

    async def __call__(
        self, request: CreateProjectTaskRequest
    ) -> CreateProjectTaskResponse:
        if not request.assignees:
            return await self._create_task_usecase(request)

        project = await self._project_queries.by_id(request.project_id.value)
        current_user = await self._current_user()
        authorize(
            CanManageProjectTask(),
            context=ProjectManagmentContext(subject=current_user, target=project),
        )
        subject_id = UserId(current_user.id_)
        subject_role = project.members[subject_id]

        subject_group_ids = await self._project_group_queries.group_ids_for_user(
            request.project_id.value, current_user.id_
        )

        permission_visitor = _ResponsiblePermissionVisitor(
            project=project,
            subject=current_user,
            subject_id=subject_id,
            subject_role=subject_role,
            subject_group_ids=subject_group_ids,
        )
        for assignee in request.assignees:
            assignee.accept(permission_visitor)

        response = await self._create_task_usecase(request)
        return CreateProjectTaskResponse(
            task_id=response["task_id"],
            project_id=response["project_id"],
            title=response["title"],
        )
