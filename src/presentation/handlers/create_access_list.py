from pydantic import UUID4

from domain.entities.access_list import AccessRule

from application.ports.gateways.query_params import (
    LikeFilter,
    OffsetPagination,
    ProjectGroupListParams,
)
from application.usecases import CreateAccessListRequest, CreateAccessListResponse
from application.compositions import CreateAccessListComposition

from presentation.models import AccessListCreate, AccessListCreated
from presentation.presenters import AccessListCreateRuleTargetPresenter, OrdersPresenter


class CreateAccessListHandler:
    def __init__(
        self,
        usecase: CreateAccessListComposition,
        rule_target_presenter: AccessListCreateRuleTargetPresenter,
        orders_presenter: OrdersPresenter,
    ):
        self._usecase = usecase
        self._rule_target_presenter = rule_target_presenter
        self._orders_presenter = orders_presenter

    async def __call__(
        self,
        request: AccessListCreate,
        project_id: UUID4,
        *,
        offset: int,
        limit: int,
        orders: str,
        name: str | None,
    ) -> AccessListCreated:

        acl_meta: CreateAccessListRequest = CreateAccessListRequest.from_primitives(
            request.name, str(project_id)
        )

        rules: list[AccessRule] = []

        for rule in request.rules:
            is_allow: bool = rule.type == "ALLOW"
            target = self._rule_target_presenter.to_domain_target(rule.target)
            rules.append(AccessRule(target, rule.action, is_allow))

        group_list_params = ProjectGroupListParams(
            filters=[LikeFilter("name", name)] if name else [],
            pagination=OffsetPagination(offset, limit),
            sorting=self._orders_presenter(orders),
        )

        response: CreateAccessListResponse = await self._usecase(
            acl_meta, rules, group_list_params
        )

        return AccessListCreated(
            id_=response["access_list_id"],
            created_by=response["owner_id"],
        )
