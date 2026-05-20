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
from presentation.presenters import AccessListCreateRuleResponsiblePresenter, OrdersPresenter


class CreateAccessListHandler:
    def __init__(
        self,
        usecase: CreateAccessListComposition,
        rule_responsible_presenter: AccessListCreateRuleResponsiblePresenter,
        orders_presenter: OrdersPresenter,
    ):
        self._usecase = usecase
        self._rule_responsible_presenter = rule_responsible_presenter
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
            responsible = self._rule_responsible_presenter.to_domain_responsible(
                rule.responsible
            )
            rules.append(AccessRule(responsible, rule.action, is_allow, order=0))

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
