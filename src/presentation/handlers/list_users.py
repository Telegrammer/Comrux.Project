from application.compositions import ListUsersComposition
from application.usecases import ListUsersElementResponse
from application.ports.gateways.query_params import (
    OrFilter,
    LikeFilter,
    UserListParams,
    OffsetPagination,
    UserFilterField,
)
from presentation.models.user import UserSearchRead
from presentation.presenters import OrdersPresenter


class ListUsersHandler:
    def __init__(
        self,
        usecase: ListUsersComposition,
        orders_presenter: OrdersPresenter,
    ):
        self._usecase = usecase
        self._presenter = orders_presenter

    async def __call__(
        self,
        search: str | None,
        raw_orders: str | None,
        offset: int,
        limit: int,
        bio_length: int = 200,
    ) -> list[UserSearchRead]:
        filters = []

        if search:
            filters.append(
                OrFilter([LikeFilter(field.value, search) for field in UserFilterField])
            )

        search_params = UserListParams(
            filters=filters,
            pagination=OffsetPagination(offset, limit),
            sorting=self._presenter(raw_orders) if raw_orders else [],
        )

        users: list[ListUsersElementResponse] = await self._usecase(search_params)
        return [
            UserSearchRead(
                id_=user["id_"],
                name=user["name"],
                email=user["email"],
                bio=user["bio"][: min(len(user["bio"]), bio_length)],
            )
            for user in users
        ]
