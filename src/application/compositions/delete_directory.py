import logging

logger = logging.getLogger(__name__)


from application.usecases import DeleteDirectoryRequest, DeleteDirectoryUsecase
from application.ports import UnitOfWork


class DeleteDirectoryComposition:

    def __init__(self, usecase: DeleteDirectoryUsecase, unit_of_work: UnitOfWork):
        self._usecase: DeleteDirectoryUsecase = usecase
        self._unit_of_work: UnitOfWork = unit_of_work

    async def __call__(self, request: DeleteDirectoryRequest) -> None:

        async with self._unit_of_work:
            logger.info("Directory %s deletion start", request.directory_id.value)
            response_message: str = await self._usecase(request)

        logger.info(response_message)
