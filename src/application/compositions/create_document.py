import logging


from domain.services import TaskService
from application.ports import UnitOfWork, TaskCommandGateway, Clock
from application.usecases import (
    CreateDocumentRequest,
    CreateDocumentUsecase,
    CreateDocumentResponse,
)

logger = logging.getLogger(__name__)


class CreateDocumentComposition:

    def __init__(
        self,
        clock: Clock,
        unit_of_work: UnitOfWork,
        usecase: CreateDocumentUsecase,
        task_service: TaskService,
        task_gateway: TaskCommandGateway,
    ):
        self._clock: Clock = clock
        self._unit_of_work: UnitOfWork = unit_of_work
        self._usecase: CreateDocumentUsecase = usecase
        self._task_gateway: TaskCommandGateway = task_gateway
        self._task_service: TaskService = task_service

    async def __call__(self, request: CreateDocumentRequest) -> CreateDocumentResponse:
        async with self._unit_of_work:
            logger.info("Document creation started")
            response: CreateDocumentResponse = await self._usecase(request)
            await self._task_gateway.add(
                self._task_service.create_task(
                    "document.created",
                    {
                        "document_id": response["content_ref"],
                        "group": request.project_id.value,
                    },
                    now=self._clock.now(),
                )
            )
        logger.info("Document %s was created", response["document"])
        return response
