__all__ = ["RemoveProjectMemberHandler"]


from pydantic import UUID4
from application.usecases import RemoveProjectMemberRequest
from application.compositions import RemoveProjectMemberComposition
from presentation.models import ProjectMemberRemove, ProjectMemberRemoved


class RemoveProjectMemberHandler:

    def __init__(self, usecase: RemoveProjectMemberComposition):
        self._usecase: RemoveProjectMemberComposition = usecase

    async def __call__(
        self, project_id: UUID4, request: ProjectMemberRemove
    ) -> ProjectMemberRemoved:

        return await self._usecase(
            RemoveProjectMemberRequest.from_primitives(
                user=str(request.user), project=str(project_id)
            )
        )
