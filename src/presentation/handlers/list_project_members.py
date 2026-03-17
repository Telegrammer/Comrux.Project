from pydantic import UUID4

from application.compositions import ListProjectMembersComposition
from application.usecases import (
    ListProjectMembersElementResponse,
    ListProjectMembersRequest,
)
from application.ports import UserListParams
from application.ports.gateways.query_params import OffsetPagination
from presentation.presenters import OrdersPresenter
from presentation.models import ProjectMemberRead


class ListProjectMembersHandler:

    def __init__(
        self, usecase: ListProjectMembersComposition, orders_presenter: OrdersPresenter
    ):
        self._usecase: ListProjectMembersComposition = usecase
        self._orders_presenter: OrdersPresenter = orders_presenter

    async def __call__(
        self, project_id: str, raw_orders: str, offset: int, limit: int
    ) -> list[ProjectMemberRead]:
        response: list[ListProjectMembersElementResponse] = await self._usecase(
            ListProjectMembersRequest.from_primitives(project_id),
            UserListParams(
                filters=[],
                pagination=OffsetPagination(offset, limit),
                sorting=self._orders_presenter(raw_orders),
            ),
        )

        return [
            ProjectMemberRead(
                user_id=UUID4(elem["user_id"]),
                name=elem["name"],
                bio=elem["bio"],
                role=elem["role"],
            )
            for elem in response
        ]
