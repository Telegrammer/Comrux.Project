__all__ = ["UpdateProjectComposition"]


import logging


from application.usecases import UpdateProjectRequest, UpdateProjectUsecase
from application.ports import UnitOfWork


logger = logging.getLogger(__name__)

class UpdateProjectComposition:

    def __init__(self, usecase: UpdateProjectUsecase, unit_of_work: UnitOfWork):
        self._usecase = usecase
        self._unit_of_work = unit_of_work
    
    async def __call__(self, request: UpdateProjectRequest) -> None:
        
        async with self._unit_of_work:
            logger.info("Project %s update start", request.project_id.value)
            await self._usecase(request)
        logger.info("Project %s updated succesfully", request.project_id.value)