"""Maps access-list rule target payloads (API) to domain AccessRuleTarget."""

from domain.entities.access_list import (
    AccessRuleGroupTarget,
    AccessRuleRoleTarget,
    AccessRuleUserTarget,
    AccessRuleTarget,
)
from domain.entities.project_group import ProjectGroupId

from presentation.models.access_list import (
    AccessRuleTargetGroupPayload,
    AccessRuleTargetRolePayload,
    AccessRuleTargetUserPayload,
)


class AccessListCreateRuleTargetPresenter:
    """Inbound counterpart to AccessListsPresenter: body → domain."""

    def to_domain_target(
        self,
        payload: AccessRuleTargetUserPayload
        | AccessRuleTargetRolePayload
        | AccessRuleTargetGroupPayload,
    ) -> AccessRuleTarget:
        match payload:
            case AccessRuleTargetUserPayload():
                return AccessRuleUserTarget(str(payload.user_id))
            case AccessRuleTargetRolePayload():
                return AccessRuleRoleTarget(role=payload.role)
            case AccessRuleTargetGroupPayload():
                return AccessRuleGroupTarget(ProjectGroupId(str(payload.group_id)))
            case _:
                raise TypeError(
                    f"Unsupported access rule target payload: {type(payload)!r}"
                )
