from pydantic import UUID4

from application.compositions import AssignAccessListComposition
from application.usecases import AssignAccessListRequest


class AssignAccessListHandler:
    def __init__(self, usecase: AssignAccessListComposition) -> None:
        self._usecase = usecase

    async def assign_to_directory(
        self,
        project_id: UUID4,
        directory_id: UUID4,
        access_list_id: UUID4 | None,
    ) -> None:
        request = AssignAccessListRequest.from_primitives(
            str(project_id),
            str(directory_id),
            str(access_list_id) if access_list_id is not None else None,
        )
        await self._usecase.assign_to_directory(request)

    async def assign_to_document(
        self,
        project_id: UUID4,
        document_id: UUID4,
        access_list_id: UUID4 | None,
    ) -> None:
        request = AssignAccessListRequest.from_primitives(
            str(project_id),
            str(document_id),
            str(access_list_id) if access_list_id is not None else None,
        )
        await self._usecase.assign_to_document(request)

