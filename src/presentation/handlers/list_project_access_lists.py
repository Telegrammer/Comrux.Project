from application.compositions import ListProjectAccessListsComposition
from application.usecases import (
    ListProjectAccessListsRequest,
    ListProjectAccessListResponse,
)
from application.ports.gateways.query_params import (
    OffsetPagination,
    AccessListsParams,
    LikeFilter,
)
from presentation.presenters import OrdersPresenter, AccessListsPresenter
from presentation.models.access_list import (
    RoleAccessRule,
    UserAccessRule,
    GroupAccessRule,
    AccessListRead,
)


class ListProjectAccessListsHandler:
    def __init__(
        self,
        usecase: ListProjectAccessListsComposition,
        orders_presenter: OrdersPresenter,
    ):
        self._usecase = usecase
        self._orders_presenter: OrdersPresenter = orders_presenter

    async def __call__(
        self,
        raw_filters: dict[str, str],
        project_id: str,
        raw_orders: str,
        offset: int,
        limit: int,
    ) -> list[AccessListRead]:

        response: ListProjectAccessListResponse = await self._usecase(
            ListProjectAccessListsRequest.from_primitives(str(project_id)),
            AccessListsParams(
                filters=[
                    LikeFilter(field_name, value)
                    for field_name, value in raw_filters.items()
                ],
                pagination=OffsetPagination(offset, limit),
                sorting=self._orders_presenter(raw_orders),
            ),
        )

        access_lists = response["access_lists"]
        user_targets = response["user_targets"]
        group_targets = response["group_targets"]
        acl_presenter: AccessListsPresenter = AccessListsPresenter(
            user_targets, group_targets
        )

        result: list[AccessListRead] = []
        for acl in access_lists:
            rules: list[UserAccessRule | RoleAccessRule | GroupAccessRule] = []
            for elem in acl["rules"]:
                acl_presenter.set_rule(elem.action, elem.is_allow)
                rules.append(elem.target.accept(acl_presenter))

            result.append(
                AccessListRead(
                    id_=acl["id_"],
                    created_by=acl["owner_id"],
                    owner_name=f"{acl['owner_name']} ({acl['owner_id'][:6]})",
                    name=acl["name"],
                    rules=rules,
                )
            )

        return result
