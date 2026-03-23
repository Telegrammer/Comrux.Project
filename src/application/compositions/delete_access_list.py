import logging


from application.ports import UnitOfWork
from application.usecases import DeleteAccessListRequest, DeleteAccessListUsecase


logger = logging.getLogger(__name__)


class DeleteAccessListComposition:

    def __init__(self, usecase: DeleteAccessListUsecase, unit_of_work: UnitOfWork):
        self._usecase = usecase
        self._unit_of_work = unit_of_work

    async def __call__(self, request: DeleteAccessListRequest) -> None:
        async with self._unit_of_work:
            logger.info(
                "Access list (%s) deletion started", request.access_list_id.value
            )
            await self._usecase(request)

        logger.info("Access list deleted")
