__all__ = ["ListCurrentUserProjectsHandler"]


from domain.enums import ProjectRole
from application.ports.gateways.query_params import (
    OffsetPagination,
    ProjectListParams,
)
from application.compositions import ListCurrentUserProjectsComposition
from application.usecases import (
    ListCurrentUserProjectsRequest,
    ListCurrentUserProjectsResponse,
)
from presentation.models import CurrentUserProjectRead
from presentation.presenters import OrdersPresenter


class ListCurrentUserProjectsHandler:

    def __init__(
        self,
        usecase: ListCurrentUserProjectsComposition,
        orders_presenter: OrdersPresenter,
    ):
        self._usecase: ListCurrentUserProjectsComposition = usecase
        self._orders_presenter: OrdersPresenter = orders_presenter

    async def __call__(
        self, role: str, raw_orders: str, offset: int, limit: int
    ) -> list[CurrentUserProjectRead]:
        response: list[ListCurrentUserProjectsResponse] = await self._usecase(
            ListCurrentUserProjectsRequest(
                role.upper() if role != "" else None,
                ProjectListParams(
                    OffsetPagination(offset, limit), self._orders_presenter(raw_orders)
                ),
            )
        )

        return [
            CurrentUserProjectRead(
                id_=elem["id_"],
                title=elem["title"],
                description=elem["description"],
                role=elem["role"] if not role else None,
                created_at=elem["created_at"],
                root_id=elem["root_id"],
            )
            for elem in response
        ]
