import logging


from application.ports import UnitOfWork
from application.usecases import (
    CreateContentTicketRequest,
    CreateContentTicketUsecase,
    CreateContentTicketResponse,
)


logger = logging.getLogger(__name__)


class CreateContentTicketComposition:

    def __init__(self, usecase: CreateContentTicketUsecase, unit_of_work: UnitOfWork):
        self._usecase: CreateContentTicketUsecase = usecase
        self._unit_of_work: UnitOfWork = unit_of_work

    async def __call__(
        self, request: CreateContentTicketRequest
    ) -> CreateContentTicketResponse:
        async with self._unit_of_work:
            logger.info(
                "Ticket for document's (%s) content creation started",
                request.document_id.value,
            )
            response: CreateContentTicketResponse = await self._usecase(request)
        logger.info("Content ticket %s was created", response["ticket_id"])
        return response
