import logging

from application.ports.gateways.query_params.user import UserListParams
from application.usecases.list_users import ListUsersElementResponse, ListUsersUsecase


logger = logging.getLogger(__name__)


class ListUsersComposition:

    def __init__(self, usecase: ListUsersUsecase):
        self._usecase = usecase

    async def __call__(
        self, search_params: UserListParams
    ) -> list[ListUsersElementResponse]:

        logger.info(
            "Fetching users from %s to %s",
            search_params.pagination.offset,
            search_params.pagination.offset + search_params.pagination.limit,
        )
        response: list[ListUsersElementResponse] = await self._usecase(search_params)
        logger.info(
            "Successfully fetched %s users",
            len(response),
        )
        return response
