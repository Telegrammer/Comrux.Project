

from application.usecases import (
    ListAccessListsUsecase,
    ListProjectAccessListsRequest,
    ListProjectAccessListResponse,
)
from application.ports.gateways.query_params import AccessListsParams


class ListProjectAccessListsComposition:

    def __init__(self, usecase: ListAccessListsUsecase):
        self._usecase = usecase

    async def __call__(
        self, request: ListProjectAccessListsRequest, search_params: AccessListsParams
    ) -> ListProjectAccessListResponse:

        response: ListProjectAccessListResponse = await self._usecase(
            request, search_params
        )

        return response
