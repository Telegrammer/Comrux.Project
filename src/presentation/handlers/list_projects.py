__all__ = ["ListProjectsHandler"]


from application.ports.gateways.query_params import (
    OffsetPagination,
    ProjectListParams,
)
from application.usecases import ListProjectsElementResponse
from application.compositions import ListProjectsComposition

from presentation.models import ProjectRead
from presentation.presenters import OrdersPresenter


class ListProjectsHandler:

    def __init__(
        self, usecase: ListProjectsComposition, orders_presenter: OrdersPresenter
    ):
        self._usecase: ListProjectsComposition = usecase
        self._orders_presenter: OrdersPresenter = orders_presenter

    async def __call__(
        self, raw_orders: str, offset: int, limit: int
    ) -> list[ProjectRead]:
        response: list[ListProjectsElementResponse] = await self._usecase(
            ProjectListParams(
                filters=[],
                pagination=OffsetPagination(offset, limit),
                sorting=self._orders_presenter(raw_orders),
            )
        )

        return [
            ProjectRead(
                id_=elem["id_"],
                title=elem["title"],
                description=elem["description"],
                owner_id=elem["owner_id"],
                owner_name=elem["owner_name"],
                members_count=elem["members_count"],
                created_at=elem["created_at"],
                root_id=elem["root_id"],
                is_private=elem["is_private"],
            )
            for elem in response
        ]
