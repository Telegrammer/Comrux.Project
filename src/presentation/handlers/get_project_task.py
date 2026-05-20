from pydantic import UUID4

from application.compositions import GetProjectTaskComposition
from application.usecases import GetProjectTaskRequest, GetProjectTaskResponse
from presentation.models import ProjectTaskAssigneeRead, ProjectTaskDetailsRead


class GetProjectTaskHandler:
    def __init__(self, usecase: GetProjectTaskComposition):
        self._usecase = usecase

    async def __call__(
        self, project_id: UUID4, task_id: UUID4
    ) -> ProjectTaskDetailsRead:
        response: GetProjectTaskResponse = await self._usecase(
            GetProjectTaskRequest.from_primitives(str(project_id), str(task_id))
        )
        assignees = [
            ProjectTaskAssigneeRead(kind="role", id_=role.value, name=role.value)
            for role in sorted(response["role_assignees"], key=lambda x: x.value)
        ]
        assignees.extend(
            ProjectTaskAssigneeRead(kind="user", id_=user_id.value, name=name.value)
            for user_id, name in response["user_assignees"].items()
        )
        assignees.extend(
            ProjectTaskAssigneeRead(
                kind="group",
                id_=group_id.value,
                name=group_assignee.name.value,
                color=group_assignee.color,
            )
            for group_id, group_assignee in response["group_assignees"].items()
        )

        return ProjectTaskDetailsRead(
            id_=response["id_"],
            project_id=response["project_id"],
            creator_id=response["creator_id"],
            creator_email=response["creator_email"],
            creator_name=response["creator_name"],
            title=response["title"],
            description=response["description"],
            status=response["status"],
            start_at=response["start_at"],
            end_at=response["end_at"],
            created_at=response["created_at"],
            updated_at=response["updated_at"],
            assignees=assignees,
        )
