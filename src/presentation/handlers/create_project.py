__all__ = ["CreateProjectHandler"]


from application.usecases import CreateProjectRequest
from application.compositions import CreateProjectComposition
from presentation.models import ProjectCreate, ProjectCreated

class CreateProjectHandler:

    def __init__(self, usecase: CreateProjectComposition):
        self._usecase: CreateProjectComposition = usecase
    
    async def __call__(self, request: ProjectCreate) -> ProjectCreated:
        return await self._usecase(CreateProjectRequest.from_primitives(**request.model_dump()))
        