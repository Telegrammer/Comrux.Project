import logging


from application.ports import UnitOfWork
from application.usecases import (
    CreateDocumentRequest,
    CreateDocumentUsecase,
    CreateDocumentResponse,
)

logger = logging.getLogger(__name__)


class CreateDocumentComposition:

    def __init__(self, usecase: CreateDocumentUsecase, unit_of_work: UnitOfWork):
        self._usecase: CreateDocumentUsecase = usecase
        self._unit_of_work: UnitOfWork = unit_of_work

    async def __call__(self, request: CreateDocumentRequest) -> CreateDocumentResponse:
        async with self._unit_of_work:
            logger.info("Document creation started")
            response: CreateDocumentResponse = await self._usecase(request)
        logger.info("Document %s was created", response['document'])
        return response
