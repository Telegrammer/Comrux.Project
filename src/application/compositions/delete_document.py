import logging

from domain.services import TaskService

from application.ports import Clock, TaskCommandGateway, UnitOfWork
from application.usecases import (
    DeleteDocumentRequest,
    DeleteDocumentResponse,
    DeleteDocumentUsecase,
)

logger = logging.getLogger(__name__)


class DeleteDocumentComposition:
    _task_type = "documents.deleted"

    def __init__(
        self,
        clock: Clock,
        usecase: DeleteDocumentUsecase,
        unit_of_work: UnitOfWork,
        task_service: TaskService,
        task_gateway: TaskCommandGateway,
    ):
        self._clock: Clock = clock
        self._usecase: DeleteDocumentUsecase = usecase
        self._unit_of_work: UnitOfWork = unit_of_work
        self._task_service: TaskService = task_service
        self._task_gateway: TaskCommandGateway = task_gateway

    async def __call__(self, request: DeleteDocumentRequest) -> None:

        async with self._unit_of_work:
            logger.info("Document %s deletion start", request.document_id.value)
            response: DeleteDocumentResponse = await self._usecase(request)
            if response.deleted and response.content_ids:
                await self._task_gateway.add(
                    self._task_service.create_task(
                        self._task_type,
                        {
                            "content_ids": [
                                content_id.value for content_id in response.content_ids
                            ],
                            "group": response.project_id.value,
                        },
                        now=self._clock.now(),
                    )
                )

        logger.info(response.message)
