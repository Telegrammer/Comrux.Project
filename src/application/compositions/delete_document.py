import logging

logger = logging.getLogger(__name__)


from application.usecases import DeleteDocumentRequest, DeleteDocumentUsecase
from application.ports import UnitOfWork


class DeleteDocumentComposition:

    def __init__(self, usecase: DeleteDocumentUsecase, unit_of_work: UnitOfWork):
        self._usecase: DeleteDocumentUsecase = usecase
        self._unit_of_work: UnitOfWork = unit_of_work

    async def __call__(self, request: DeleteDocumentRequest) -> None:

        async with self._unit_of_work:
            logger.info("Document %s deletion start", request.document_id.value)
            response_message: str = await self._usecase(request)

        logger.info(response_message)
