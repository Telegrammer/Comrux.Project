from pydantic import UUID4

from application.compositions import ListProjectGroupMembersComposition
from application.ports import UserListParams
from application.ports.gateways.query_params import OffsetPagination
from application.usecases import (
    ListProjectGroupMembersElementResponse,
    ListProjectGroupMembersRequest,
)
from presentation.models import ProjectMemberRead
from presentation.presenters import OrdersPresenter


class ListProjectGroupMembersHandler:
    def __init__(
        self,
        usecase: ListProjectGroupMembersComposition,
        orders_presenter: OrdersPresenter,
    ) -> None:
        self._usecase = usecase
        self._orders_presenter = orders_presenter

    async def __call__(
        self,
        project_id: UUID4,
        group_id: UUID4,
        raw_orders: str,
        offset: int,
        limit: int,
    ) -> list[ProjectMemberRead]:
        response: list[ListProjectGroupMembersElementResponse] = await self._usecase(
            ListProjectGroupMembersRequest.from_primitives(
                project_id=str(project_id),
                group_id=str(group_id),
            ),
            UserListParams(
                filters=[],
                pagination=OffsetPagination(offset, limit),
                sorting=self._orders_presenter(raw_orders),
            ),
        )
        return [
            ProjectMemberRead(
                user_id=item["user_id"],
                name=item["name"],
                bio=item["bio"],
                role=item["role"],
            )
            for item in response
        ]
