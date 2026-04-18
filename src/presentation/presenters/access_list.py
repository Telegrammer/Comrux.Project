from domain.enums import ProjectUnitAction
from domain.entities.user import UserId
from domain.entities.project_group import ProjectGroupId
from domain.value_objects import Name
from domain.entities.access_list import (
    AccessRuleTargetVisitor,
    AccessRuleGroupTarget,
    AccessRuleUserTarget,
    AccessRuleRoleTarget,
)

from presentation.models.access_list import UserAccessRule, RoleAccessRule, GroupAccessRule


class AccessListsPresenter(AccessRuleTargetVisitor):
    def __init__(
        self,
        user_names: dict[UserId, Name],
        group_names: dict[ProjectGroupId, Name],
    ):
        self._names = user_names
        self._group_names = group_names
        self._action: ProjectUnitAction | None = None
        self._type: str | None = None

    def visit_role(self, target: AccessRuleRoleTarget) -> RoleAccessRule:
        return RoleAccessRule(action=self._action, type=self._type, target=target.role)

    def visit_user(self, target: AccessRuleUserTarget) -> UserAccessRule:
        user_id: UserId = target.user_id
        return UserAccessRule(
            action=self._action,
            type=self._type,
            target=user_id.value,
            display_name=f"{self._names[user_id].value} ({target.user_id.value[:6]})",
        )

    def visit_group(self, target: AccessRuleGroupTarget) -> GroupAccessRule:
        group_id = target.group_id
        title = self._group_names.get(group_id, Name("."))
        return GroupAccessRule(
            action=self._action,
            type=self._type,
            target=group_id.value,
            display_name=f"{title.value} ({group_id.value[:6]})",
        )

    def set_rule(self, action: ProjectUnitAction, is_allow: bool) -> None:
        self._action = action
        self._type = "ALLOW" if is_allow else "DENY"
