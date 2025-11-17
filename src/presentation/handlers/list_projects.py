__all__ = ["ListProjectsHandler"]


from application.ports.gateways.query_params import (
    SortingParam,
    OffsetPagination,
    ProjectListParams,
)
from application.usecases import (
    ListProjectsUsecase,
    ListProjectsElementResponse,
)

from presentation.models import ProjectRead
from presentation.presenters import OrdersPresenter


class ListProjectsHandler:

    def __init__(self, usecase: ListProjectsUsecase, orders_presenter: OrdersPresenter):
        self._usecase: ListProjectsUsecase = usecase
        self._orders_presenter: OrdersPresenter = orders_presenter

    async def __call__(
        self, raw_orders: str, offset: int, limit: int
    ) -> list[ProjectRead]:
        response: list[ListProjectsElementResponse] = await self._usecase(
            ProjectListParams(
                OffsetPagination(offset, limit), self._orders_presenter(raw_orders)
            )
        )

        return [
            ProjectRead(
                id_=elem["id_"],
                title=elem["title"],
                description=elem["description"],
                created_at=elem["created_at"],
            )
            for elem in response
        ]
