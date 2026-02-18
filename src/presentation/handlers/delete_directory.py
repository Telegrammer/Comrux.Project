from pydantic import UUID4
from application.usecases import DeleteDirectoryRequest
from application.compositions import DeleteDirectoryComposition


class DeleteDirectoryHandler:

    def __init__(self, usecase: DeleteDirectoryComposition):
        self._usecase = usecase

    async def __call__(self, project_id: UUID4, directory_id: UUID4) -> None:
        await self._usecase(
            DeleteDirectoryRequest.from_primitives(str(project_id), str(directory_id))
        )
