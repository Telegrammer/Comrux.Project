from functools import singledispatchmethod
from typing import Sequence

from domain.entities import AccessList, AccessRule, AccessListId, ProjectId, UserId
from domain.entities.project_group import ProjectGroupId
from domain.entities.access_list import (
    AccessRuleTarget,
    AccessRuleGroupTarget,
    AccessRuleRoleTarget,
    AccessRuleUserTarget,
)
from domain.value_objects import FileName, Name
from application.models import ProjectAccessListsRead
from application.ports.mappers import AccessListMapper, MappingError
from infrastructure.models import (
    AccessList as OrmAccessList,
    AccessRule as OrmAccessRule,
    AccessRuleUserTarget as OrmUserTarget,
    AccessRuleRoleTarget as OrmRoleTarget,
    AccessRuleGroupTarget as OrmGroupTarget,
)

from infrastructure.adapters.access_rule_target_collector import (
    SqlAlchemyAccessRuleTargetCollector,
)


class SqlAlchemyAccessListMapper(AccessListMapper[OrmAccessList]):
    def __init__(self):
        self._user_names: dict[UserId, Name] = {}
        self._group_names: dict[ProjectGroupId, Name] = {}

    @singledispatchmethod
    def _target_to_domain(self, orm_target: AccessRuleTarget):
        raise MappingError(f"Unknown target type: {type(orm_target)}")

    @_target_to_domain.register
    def _(self, orm_target: OrmUserTarget) -> AccessRuleUserTarget:

        value: str = str(orm_target.user_id)
        self._user_names[UserId(value)] = Name(orm_target.user.name)
        return AccessRuleUserTarget(value)

    @_target_to_domain.register
    def _(self, orm_target: OrmRoleTarget) -> AccessRuleRoleTarget:
        return AccessRuleRoleTarget(role=orm_target.role)

    @_target_to_domain.register
    def _(self, orm_target: OrmGroupTarget) -> AccessRuleGroupTarget:
        gid = ProjectGroupId(str(orm_target.group_id))
        group_name = (
            Name(orm_target.group.name) if orm_target.group is not None else Name(".")
        )
        self._group_names[gid] = group_name
        return AccessRuleGroupTarget(gid)

    def to_domain(self, dto: OrmAccessList) -> AccessList:
        return AccessList(
            id_=AccessListId(str(dto.id_)),
            name=FileName(dto.name),
            project=ProjectId(str(dto.project_id)),
            owner=UserId(str(dto.owner)),
            rules=[
                AccessRule(
                    target=self._target_to_domain(rule.target),
                    action=rule.action,
                    is_allow=rule.is_allow,
                )
                for rule in dto.rules
            ],
        )

    def to_dto(
        self, entity: AccessList, visitor: SqlAlchemyAccessRuleTargetCollector
    ) -> OrmAccessList:

        return OrmAccessList(
            id_=entity.id_,
            name=entity.name,
            owner=entity.owner,
            project_id=entity.project,
            rules=[
                OrmAccessRule(
                    target_id=visitor.resolve(rule.target),
                    action=rule.action,
                    is_allow=rule.is_allow,
                )
                for rule in entity.rules
            ],
        )

    def to_list_model(
        self, query_result: Sequence[tuple[OrmAccessList, str]]
    ) -> ProjectAccessListsRead:

        access_lists: list[AccessList] = []
        owners: list[Name | None] = []
        self._user_names = {}
        self._group_names = {}

        for acl, owner in query_result:
            access_lists.append(self.to_domain(acl))
            owners.append(Name(owner) if owner else None)

        return ProjectAccessListsRead(
            access_lists=access_lists,
            owners=owners,
            user_targets=self._user_names,
            group_targets=self._group_names,
        )
