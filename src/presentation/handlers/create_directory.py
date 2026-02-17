from pydantic import UUID4
from application.usecases import CreateDirectoryRequest, CreateDirectoryResponse
from application.compositions import CreateDirectoryComposition
from presentation.models import DirectoryCreate, DirectoryCreated


class CreateDirectoryHandler:

    def __init__(self, usecase: CreateDirectoryComposition):
        self._usecase: CreateDirectoryComposition = usecase

    async def __call__(
        self, project_id: UUID4, request: DirectoryCreate
    ) -> DirectoryCreated:
        response: CreateDirectoryResponse = await self._usecase(
            CreateDirectoryRequest.from_primitives(
                str(project_id), str(request.parent_id), request.name
            )
        )
        return DirectoryCreated(
            id_=response['directory']
        )
