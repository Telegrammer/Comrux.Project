from pydantic import UUID4
from application.usecases import DeleteAccessListRequest
from application.compositions import DeleteAccessListComposition


class DeleteAccessListHandler:

    def __init__(self, usecase: DeleteAccessListComposition):
        self._usecase = usecase

    async def __call__(self, project_id: UUID4, access_list_id: UUID4) -> None:
        await self._usecase(
            DeleteAccessListRequest.from_primitives(
                str(project_id), str(access_list_id)
            )
        )
