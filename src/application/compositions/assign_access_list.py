import logging

from application.ports import UnitOfWork
from application.usecases import (
    AssignAccessListRequest,
    AssignAccessListToDirectoryUsecase,
    AssignAccessListToDocumentUsecase,
)

logger = logging.getLogger(__name__)


class AssignAccessListComposition:
    def __init__(
        self,
        assign_to_directory_usecase: AssignAccessListToDirectoryUsecase,
        assign_to_document_usecase: AssignAccessListToDocumentUsecase,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._assign_to_directory_usecase = assign_to_directory_usecase
        self._assign_to_document_usecase = assign_to_document_usecase
        self._unit_of_work = unit_of_work

    async def assign_to_directory(self, request: AssignAccessListRequest) -> None:
        async with self._unit_of_work:
            logger.info(
                "ACL assignment to directory started: unit=%s project=%s",
                request.unit_id.value,
                request.project_id.value,
            )
            await self._assign_to_directory_usecase(request)
        logger.info("ACL assignment to directory finished")

    async def assign_to_document(self, request: AssignAccessListRequest) -> None:
        async with self._unit_of_work:
            logger.info(
                "ACL assignment to document started: unit=%s project=%s",
                request.unit_id.value,
                request.project_id.value,
            )
            await self._assign_to_document_usecase(request)
        logger.info("ACL assignment to document finished")

