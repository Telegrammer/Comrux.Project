from pydantic import UUID4

from application.usecases import GetDocumentContentRequest, GetDocumentContentUsecase


class GetDocumentContentHandler:

    def __init__(self, usecase: GetDocumentContentUsecase):
        self._usecase: GetDocumentContentUsecase = usecase

    async def __call__(self, project_id: UUID4, document_id: UUID4) -> bytes:
        return await self._usecase(
            GetDocumentContentRequest.from_primitives(
                str(project_id), str(document_id)
            )
        )
