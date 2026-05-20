from pydantic import UUID4

from application.compositions import ListProjectTasksComposition
from application.ports.gateways.query_params import (
    EqFilter,
    InFilter,
    LikeFilter,
    OffsetPagination,
    ProjectTaskListParams,
)
from application.usecases import (
    ListProjectTasksRequest,
    ListProjectTasksElementResponse,
)
from presentation.models import ProjectTaskRead
from presentation.presenters import OrdersPresenter


class ListProjectTasksHandler:
    def __init__(
        self,
        usecase: ListProjectTasksComposition,
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
        status: str | None = None,
        scope: str | None = None,
    ) -> list[ProjectTaskRead]:
        filters = [EqFilter("status", status)] if status else []
        if name:
            filters.append(LikeFilter("title", name))
        mine = False
        if scope == "mine":
            mine = True
        elif scope == "active":
            filters.append(InFilter("status", ["PLANNED", "IN_PROGRESS"]))
        elif scope == "overdue":
            filters.append(EqFilter("status", "OVERDUE"))
        response: list[ListProjectTasksElementResponse] = await self._usecase(
            ListProjectTasksRequest.from_primitives(str(project_id)),
            ProjectTaskListParams(
                filters=filters,
                pagination=OffsetPagination(offset, limit),
                sorting=self._orders_presenter(raw_orders),
                mine=mine,
            ),
        )
        return [
            ProjectTaskRead(
                id_=item["id_"],
                title=item["title"],
                description=item["description"],
                status=item["status"],
            )
            for item in response
        ]
