from pydantic import UUID4

from application.compositions import ListProjectGroupsComposition
from application.ports.gateways.query_params import (
    LikeFilter,
    OffsetPagination,
    ProjectGroupListParams,
)
from application.usecases import (
    ListProjectGroupsElementResponse,
    ListProjectGroupsRequest,
)
from presentation.models import ProjectGroupRead
from presentation.presenters import OrdersPresenter


class ListProjectGroupsHandler:
    def __init__(
        self,
        usecase: ListProjectGroupsComposition,
        orders_presenter: OrdersPresenter,
    ):
        self._usecase = usecase
        self._orders_presenter = orders_presenter

    async def __call__(
        self,
        project_id: UUID4,
        raw_orders: str,
        offset: int,
        limit: int,
        name: str | None = None,
    ) -> list[ProjectGroupRead]:
        filters = [LikeFilter("name", name)] if name else []
        response: list[ListProjectGroupsElementResponse] = await self._usecase(
            ListProjectGroupsRequest.from_primitives(str(project_id)),
            ProjectGroupListParams(
                filters=filters,
                pagination=OffsetPagination(offset, limit),
                sorting=self._orders_presenter(raw_orders),
            ),
        )
        return [
            ProjectGroupRead(
                id_=item["id_"],
                name=item["name"],
                color=item["color"],
                owner=item["owner"],
                is_public=item["is_public"],
                participants_count=item["participants_count"],
            )
            for item in response
        ]
