from pydantic import UUID4

from application.compositions import CreateProjectTaskComposition
from application.usecases import CreateProjectTaskRequest, CreateProjectTaskResponse
from presentation.models import ProjectTaskCreate, ProjectTaskCreated
from presentation.presenters import ProjectTaskAssigneePresenter


class CreateProjectTaskHandler:
    def __init__(
        self,
        composition: CreateProjectTaskComposition,
        assignee_presenter: ProjectTaskAssigneePresenter,
    ) -> None:
        self._composition = composition
        self._assignee_presenter = assignee_presenter

    async def __call__(
        self, project_id: UUID4, request_body: ProjectTaskCreate
    ) -> ProjectTaskCreated:
        assignees = [
            self._assignee_presenter.to_domain_assignee(item)
            for item in request_body.assignees
        ]
        response: CreateProjectTaskResponse = await self._composition(
            CreateProjectTaskRequest.from_primitives(
                project_id=str(project_id),
                title=request_body.title,
                description=request_body.description,
                start_at=request_body.start_at,
                end_at=request_body.end_at,
                assignees=assignees,
            )
        )
        return ProjectTaskCreated(
            task_id=response["task_id"],
            project_id=response["project_id"].value,
        )
