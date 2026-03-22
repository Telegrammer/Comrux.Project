from pydantic import UUID4


from domain.enums import ProjectRole
from domain.entities.access_list import (
    AccessRule,
    AccessRuleRoleTarget,
    AccessRuleUserTarget,
    AccessRuleTarget,
)

from application.usecases import CreateAccessListRequest, CreateAccessListResponse
from application.compositions import CreateAccessListComposition


from presentation.models import AccessListCreate, AccessListCreated


class CreateAccessListHandler:

    def __init__(self, usecase: CreateAccessListComposition):
        self._usecase = usecase

    async def __call__(
        self, request: AccessListCreate, project_id: UUID4
    ) -> AccessListCreated:

        acl_meta: CreateAccessListRequest = CreateAccessListRequest.from_primitives(
            request.name, str(project_id)
        )

        rules: list[AccessRuleTarget] = []

        for rule in request.rules:
            is_allow: bool = rule.type == "ALLOW"
            target: AccessRuleTarget = (
                AccessRuleRoleTarget(rule.target)
                if rule.target in ProjectRole
                else AccessRuleUserTarget(rule.target)
            )
            rules.append(AccessRule(target, rule.action, is_allow))

        response: CreateAccessListResponse = await self._usecase(acl_meta, rules)

        return AccessListCreated(
            id_=response["access_list_id"],
            created_by=response["owner_id"],
        )
