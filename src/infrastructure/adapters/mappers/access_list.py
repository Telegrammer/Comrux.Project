from functools import singledispatchmethod
from typing import Sequence

from domain.entities import AccessList, AccessRule, AccessListId, ProjectId, UserId
from domain.entities.project_group import ProjectGroupId
from domain.entities.access_list import (
    AccessRuleResponsible,
    AccessRuleGroupResponsible,
    AccessRuleRoleResponsible,
    AccessRuleUserResponsible,
)
from domain.value_objects import FileName, Name
from application.models import ProjectAccessListsRead
from application.ports.mappers import AccessListMapper, MappingError
from infrastructure.models import (
    AccessList as OrmAccessList,
    AccessRule as OrmAccessRule,
    AccessRuleUserResponsible as OrmUserResponsible,
    AccessRuleRoleResponsible as OrmRoleResponsible,
    AccessRuleGroupResponsible as OrmGroupResponsible,
)

from infrastructure.adapters.responsible_collector import SqlAlchemyResponsibleCollector


class SqlAlchemyAccessListMapper(AccessListMapper[OrmAccessList]):
    def __init__(self):
        self._user_names: dict[UserId, Name] = {}
        self._group_names: dict[ProjectGroupId, Name] = {}

    @singledispatchmethod
    def _responsible_to_domain(self, orm_responsible: AccessRuleResponsible):
        raise MappingError(f"Unknown responsible type: {type(orm_responsible)}")

    @_responsible_to_domain.register
    def _(self, orm_responsible: OrmUserResponsible) -> AccessRuleUserResponsible:

        value: str = str(orm_responsible.user_id)
        self._user_names[UserId(value)] = Name(orm_responsible.user.name)
        return AccessRuleUserResponsible(value)

    @_responsible_to_domain.register
    def _(self, orm_responsible: OrmRoleResponsible) -> AccessRuleRoleResponsible:
        return AccessRuleRoleResponsible(role=orm_responsible.role)

    @_responsible_to_domain.register
    def _(self, orm_responsible: OrmGroupResponsible) -> AccessRuleGroupResponsible:
        gid = ProjectGroupId(str(orm_responsible.group_id))
        group_name = (
            Name(orm_responsible.group.name)
            if orm_responsible.group is not None
            else Name(".")
        )
        self._group_names[gid] = group_name
        return AccessRuleGroupResponsible(gid)

    def to_domain(self, dto: OrmAccessList) -> AccessList:
        return AccessList(
            id_=AccessListId(str(dto.id_)),
            name=FileName(dto.name),
            project=ProjectId(str(dto.project_id)),
            owner=UserId(str(dto.owner)),
            rules=[
                AccessRule(
                    responsible=self._responsible_to_domain(rule.responsible),
                    action=rule.action,
                    is_allow=rule.is_allow,
                    order=rule.order,
                )
                for rule in dto.rules
            ],
        )

    def to_dto(
        self, entity: AccessList, visitor: SqlAlchemyResponsibleCollector
    ) -> OrmAccessList:

        return OrmAccessList(
            id_=entity.id_,
            name=entity.name,
            owner=entity.owner,
            project_id=entity.project,
            rules=[
                OrmAccessRule(
                    responsible_id=visitor.resolve(rule.responsible),
                    action=rule.action,
                    is_allow=rule.is_allow,
                    order=rule.order,
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
            user_responsibles=self._user_names,
            group_responsibles=self._group_names,
        )
