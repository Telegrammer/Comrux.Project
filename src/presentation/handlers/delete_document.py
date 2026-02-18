from pydantic import UUID4
from application.usecases import DeleteDocumentRequest
from application.compositions import DeleteDocumentComposition


class DeleteDocumentHandler:

    def __init__(self, usecase: DeleteDocumentComposition):
        self._usecase = usecase

    async def __call__(self, project_id: UUID4, document_id: UUID4) -> None:
        await self._usecase(
            DeleteDocumentRequest.from_primitives(str(project_id), str(document_id))
        )
