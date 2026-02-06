__all__ = ["AddProjectMemberHandler"]


from pydantic import UUID4
from application.usecases import AddProjectMemberRequest
from application.compositions import AddProjectMemberComposition
from presentation.models import ProjectMemberAdd, ProjectMemberAdded


class AddProjectMemberHandler:

    def __init__(self, usecase: AddProjectMemberComposition):
        self._usecase: AddProjectMemberComposition = usecase

    async def __call__(
        self, project_id: UUID4, request: ProjectMemberAdd
    ) -> ProjectMemberAdded:

        return await self._usecase(
            AddProjectMemberRequest.from_primitives(
                user=str(request.user), project=str(project_id)
            )
        )
