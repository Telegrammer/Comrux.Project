__all__ = ["ListCurrentUserProjectsComposition"]


import logging
from application.usecases import (
    ListCurrentUserProjectsRequest,
    ListCurrentUserProjectsUsecase,
    ListCurrentUserProjectsResponse,
)
from application.services import CurrentUserService


logger = logging.getLogger(__name__)


class ListCurrentUserProjectsComposition:

    def __init__(
        self, usecase: ListCurrentUserProjectsUsecase, current_user: CurrentUserService
    ):
        self._usecase: ListCurrentUserProjectsUsecase = usecase
        self._current_user: CurrentUserService = current_user

    async def __call__(
        self, request: ListCurrentUserProjectsRequest
    ) -> list[ListCurrentUserProjectsResponse]:
        current_user = await self._current_user()
        logger.info(
            "Fetching projects by user %s (%s)", current_user.id_, current_user.name
        )
        response: list[ListCurrentUserProjectsResponse] = await self._usecase(request)
        logger.info("Successfully fetched %s projects", len(response))
        return response
