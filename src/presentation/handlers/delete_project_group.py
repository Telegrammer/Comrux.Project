from pydantic import UUID4

from application.compositions import DeleteProjectGroupComposition
from application.usecases import DeleteProjectGroupRequest


class DeleteProjectGroupHandler:
    def __init__(self, usecase: DeleteProjectGroupComposition):
        self._usecase = usecase

    async def __call__(self, project_id: UUID4, group_id: UUID4) -> None:
        await self._usecase(
            DeleteProjectGroupRequest.from_primitives(
                project_id=str(project_id),
                group_id=str(group_id),
            )
        )
