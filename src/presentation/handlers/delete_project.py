__all__ = ["DeleteProjectHandler"]


from application.usecases import DeleteProjectRequest
from application.compositions import DeleteProjectComposition

class DeleteProjectHandler:

    def __init__(self, usecase: DeleteProjectComposition):
        self._usecase: DeleteProjectComposition = usecase
    
    async def __call__(self, request: str):
        await self._usecase(DeleteProjectRequest.from_primitives(request))