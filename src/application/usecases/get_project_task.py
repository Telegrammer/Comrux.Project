from dataclasses import dataclass
from datetime import datetime
from typing import TypedDict

from application.exceptions import ProjectTaskNotInProjectError
from application.models import ProjectTaskGroupAssigneeRead
from application.ports import Clock
from application.ports.authorization import (
    CanManageProjectContent,
    ProjectContentManagmentContext,
    authorize,
)
from application.ports.gateways import ProjectQueryGateway, UserQueryGateway
from application.ports.gateways.project_task import (
    ProjectTaskCommandGateway,
    ProjectTaskQueryGateway,
)
from application.services import CurrentUserService
from domain.entities import ProjectId, ProjectTask, ProjectTaskId, User, UserId
from domain.entities.project_group import ProjectGroupId
from domain.enums import ProjectRole, ProjectTaskStatus
from domain.value_objects import EmailAddress, Name


@dataclass
class GetProjectTaskRequest:
    project_id: ProjectId
    task_id: ProjectTaskId

    @classmethod
    def from_primitives(cls, project_id: str, task_id: str) -> "GetProjectTaskRequest":
        return cls(project_id=ProjectId(project_id), task_id=ProjectTaskId(task_id))


class GetProjectTaskResponse(TypedDict):
    id_: str
    project_id: str
    creator_id: str
    title: str
    description: str
    creator_email: EmailAddress
    creator_name: Name
    status: ProjectTaskStatus
    start_at: datetime
    end_at: datetime
    created_at: datetime
    updated_at: datetime
    role_assignees: set[ProjectRole]
    user_assignees: dict[UserId, Name]
    group_assignees: dict[ProjectGroupId, ProjectTaskGroupAssigneeRead]

    @classmethod
    def from_entity(
        cls,
        task: ProjectTask,
        task_creator: User,
        role_assignees: set[ProjectRole],
        user_assignees: dict[UserId, Name],
        group_assignees: dict[ProjectGroupId, ProjectTaskGroupAssigneeRead],
    ) -> "GetProjectTaskResponse":
        return cls(
            id_=task.id_,
            project_id=task.project_id.value,
            creator_id=task.creator_id.value,
            title=task.title,
            description=task.description,
            creator_email=task_creator.email,
            creator_name=task_creator.name,
            status=task.status,
            start_at=task.start_at,
            end_at=task.end_at,
            created_at=task.created_at,
            updated_at=task.updated_at,
            role_assignees=role_assignees,
            user_assignees=user_assignees,
            group_assignees=group_assignees,
        )


class GetProjectTaskUsecase:
    def __init__(
        self,
        clock: Clock,
        task_commands: ProjectTaskCommandGateway,
        task_queries: ProjectTaskQueryGateway,
        current_user: CurrentUserService,
        project_gateway: ProjectQueryGateway,
        user_gateway: UserQueryGateway,
    ):
        self._clock = clock
        self._task_commands = task_commands
        self._task_queries = task_queries
        self._current_user = current_user
        self._project_gateway = project_gateway
        self._user_gateway = user_gateway

    async def __call__(self, request: GetProjectTaskRequest) -> GetProjectTaskResponse:
        now: datetime = self._clock.now()
        found_project = await self._project_gateway.by_id(request.project_id.value)
        current_user = await self._current_user()

        authorize(
            CanManageProjectContent(),
            context=ProjectContentManagmentContext(
                subject=current_user, target=found_project
            ),
        )

        await self._task_commands.sync_overdue_batch(request.project_id.value, now)
        task_details = await self._task_queries.by_id_detailed(request.task_id.value)
        if task_details.task.project_id.value != found_project.id_:
            raise ProjectTaskNotInProjectError(
                "Given task is not pinned to given project"
            )
        task_creator = await self._user_gateway.by_id(
            task_details.task.creator_id.value
        )

        return GetProjectTaskResponse.from_entity(
            task_details.task,
            task_creator,
            task_details.role_assignees,
            task_details.user_assignees,
            task_details.group_assignees,
        )
