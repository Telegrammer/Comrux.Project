from dataclasses import dataclass
from typing import TypedDict

from application.ports.authorization import (
    CanManageProjectContent,
    ProjectContentManagmentContext,
    authorize,
)
from application.ports import Clock
from application.ports.gateways import (
    ProjectQueryGateway,
    ProjectTaskCommandGateway,
    ProjectTaskQueryGateway,
)
from application.ports.gateways.query_params import ProjectTaskListParams
from application.services import CurrentUserService
from domain.entities import ProjectId, ProjectTask, ProjectTaskId
from domain.enums import ProjectTaskStatus


@dataclass
class ListProjectTasksRequest:
    project_id: ProjectId

    @classmethod
    def from_primitives(cls, project_id: str) -> "ListProjectTasksRequest":
        return cls(project_id=ProjectId(project_id))


class ListProjectTasksElementResponse(TypedDict):
    id_: ProjectTaskId
    title: str
    description: str
    status: ProjectTaskStatus

    @classmethod
    def from_entity(cls, task: ProjectTask) -> "ListProjectTasksElementResponse":
        return cls(
            id_=task.id_,
            title=task.title,
            description=task.description,
            status=task.status,
        )


class ListProjectTasksUsecase:
    def __init__(
        self,
        clock: Clock,
        current_user: CurrentUserService,
        project_queries: ProjectQueryGateway,
        task_commands: ProjectTaskCommandGateway,
        task_queries: ProjectTaskQueryGateway,
    ) -> None:
        self._clock = clock
        self._current_user = current_user
        self._project_queries = project_queries
        self._task_commands = task_commands
        self._task_queries = task_queries

    async def __call__(
        self, request: ListProjectTasksRequest, params: ProjectTaskListParams
    ) -> list[ListProjectTasksElementResponse]:
        current_user = await self._current_user()
        project = await self._project_queries.by_id(request.project_id.value)
        authorize(
            CanManageProjectContent(),
            context=ProjectContentManagmentContext(
                subject=current_user,
                target=project,
            ),
        )
        if params.mine:
            params = ProjectTaskListParams(
                filters=params.filters,
                pagination=params.pagination,
                sorting=params.sorting,
                assigned_to_user_id=current_user.id_,
                mine=False,
            )
        await self._task_commands.sync_overdue_batch(
            request.project_id.value, self._clock.now()
        )
        tasks = await self._task_queries.by_project(request.project_id.value, params)
        return [ListProjectTasksElementResponse.from_entity(task) for task in tasks]
