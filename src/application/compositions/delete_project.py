__all__ = ["DeleteProjectComposition"]


import logging


from application.usecases import (
    DeleteProjectUsecase,
    DeleteProjectRequest,
)
from application.ports import UnitOfWork


logger = logging.getLogger(__name__)


class DeleteProjectComposition:

    def __init__(self, usecase: DeleteProjectUsecase, unit_of_work: UnitOfWork):
        self._usecase = usecase
        self._unit_of_work = unit_of_work

    async def __call__(self, request: DeleteProjectRequest) -> None:

        async with self._unit_of_work:
            logger.info("Project %s deletion start", request.project_id.value)
            await self._usecase(request)
        logger.info("Project %s deleted succesfully", request.project_id.value)
