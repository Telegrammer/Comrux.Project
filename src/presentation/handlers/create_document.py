from pydantic import UUID4
from application.usecases import CreateDocumentRequest, CreateDocumentResponse
from application.compositions import CreateDocumentComposition
from presentation.models import DocumentCreate, DocumentCreated


class CreateDocumentHandler:

    def __init__(self, usecase: CreateDocumentComposition):
        self._usecase: CreateDocumentComposition = usecase

    async def __call__(
        self, project_id: UUID4, request: DocumentCreate
    ) -> DocumentCreated:
        response: CreateDocumentResponse = await self._usecase(
            CreateDocumentRequest.from_primitives(
                str(project_id), str(request.parent_id), request.name
            )
        )
        return DocumentCreated(
            id_=response["document"], content_ref=response["content_ref"]
        )
