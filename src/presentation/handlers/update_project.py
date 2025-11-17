__all__ = ["UpdateProjectHandler"]


from application.usecases import UpdateProjectRequest
from application.compositions import UpdateProjectComposition
from presentation.models import ProjectUpdate


class UpdateProjectHandler:

    def __init__(self, usecase: UpdateProjectComposition):
        self._usecase = usecase

    async def __call__(self, project_id: str, request: ProjectUpdate) -> None:
        await self._usecase(
            UpdateProjectRequest.from_primitives(
                project_id,
                request.title,
                request.description,
            )
        )
