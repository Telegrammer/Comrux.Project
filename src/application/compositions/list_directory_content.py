import logging

from domain.ports import ProjectUnitVisitor


from application.usecases import (
    ListDirectoryContentRequest,
    ListDirectoryContentUsecase,
)
from application.ports.gateways.query_params import ProjectUnitListParams


logger = logging.getLogger(__name__)


class ListDirectoryContentCompostion:

    def __init__(self, usecase: ListDirectoryContentUsecase):
        self._usecase: ListDirectoryContentUsecase = usecase

    async def __call__(
        self,
        unit_visitor: ProjectUnitVisitor,
        request: ListDirectoryContentRequest,
        search_params: ProjectUnitListParams,
    ) -> None:

        logger.info(
            "Fetching content of project's directory %s",
            request.parent_id.value,
        )
        await self._usecase(unit_visitor, request, search_params)

        logger.info(
            "Successfully fetched %s elements of directory",
            unit_visitor.count_visited(),
        )
