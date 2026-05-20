"""Maps access-list rule responsible payloads (API) to domain responsible."""

from domain.entities.access_list import (
    AccessRuleGroupResponsible,
    AccessRuleRoleResponsible,
    AccessRuleUserResponsible,
    AccessRuleResponsible,
)
from domain.entities.project_group import ProjectGroupId

from presentation.models.access_list import (
    AccessRuleResponsibleGroupPayload,
    AccessRuleResponsibleRolePayload,
    AccessRuleResponsibleUserPayload,
)


class AccessListCreateRuleResponsiblePresenter:
    """Inbound counterpart to AccessListsPresenter: body -> domain."""

    def to_domain_responsible(
        self,
        payload: AccessRuleResponsibleUserPayload
        | AccessRuleResponsibleRolePayload
        | AccessRuleResponsibleGroupPayload,
    ) -> AccessRuleResponsible:
        match payload:
            case AccessRuleResponsibleUserPayload():
                return AccessRuleUserResponsible(str(payload.user_id))
            case AccessRuleResponsibleRolePayload():
                return AccessRuleRoleResponsible(role=payload.role)
            case AccessRuleResponsibleGroupPayload():
                return AccessRuleGroupResponsible(ProjectGroupId(str(payload.group_id)))
            case _:
                raise TypeError(
                    f"Unsupported access rule responsible payload: {type(payload)!r}"
                )
