import logging


from domain.entities import AccessRule
from application.ports import UnitOfWork
from application.ports.gateways.query_params import ProjectGroupListParams
from application.usecases import (
    CreateAccessListRequest,
    CreateAccessListUsecase,
    CreateAccessListResponse,
)


logger = logging.getLogger(__name__)


class CreateAccessListComposition:

    def __init__(self, usecase: CreateAccessListUsecase, unit_of_work: UnitOfWork):
        self._usecase = usecase
        self._unit_of_work = unit_of_work

    async def __call__(
        self,
        request: CreateAccessListRequest,
        rules: list[AccessRule],
        project_group_list_params: ProjectGroupListParams,
    ) -> CreateAccessListResponse:
        async with self._unit_of_work:
            logger.info(
                "Access list for (%s) project creation started",
                request.project_id.value,
            )
            response: CreateAccessListResponse = await self._usecase(
                request, rules, project_group_list_params
            )
        logger.info(
            "Access list %s was created by %s",
            response["access_list_id"],
            response["owner_id"],
        )
        return response
