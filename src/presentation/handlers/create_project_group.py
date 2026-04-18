from pydantic import UUID4

from application.compositions import CreateProjectGroupComposition
from application.usecases import CreateProjectGroupRequest, CreateProjectGroupResponse
from presentation.models import ProjectGroupCreate, ProjectGroupCreated


class CreateProjectGroupHandler:
    def __init__(self, usecase: CreateProjectGroupComposition):
        self._usecase = usecase

    async def __call__(
        self, project_id: UUID4, request_body: ProjectGroupCreate
    ) -> ProjectGroupCreated:
        response: CreateProjectGroupResponse = await self._usecase(
            CreateProjectGroupRequest.from_primitives(
                project_id=str(project_id),
                name=request_body.name,
                color=request_body.color,
                is_public=request_body.is_public,
                participants=[str(item) for item in request_body.participants],
            )
        )
        return ProjectGroupCreated(
            group_id=response["group_id"],
            owner_id=response["owner_id"],
            project_id=response["project_id"],
        )
