from dataclasses import dataclass, field

from ..enums import ProjectUnitAction
from ..value_objects import Uuid4, FileName
from .base import AggregationRoot
from .project import ProjectId
from .user import UserId
from .responsible import (
    Responsible as AccessRuleResponsible,
    ResponsibleVisitor as AccessRuleResponsibleVisitor,
    UserResponsible as AccessRuleUserResponsible,
    RoleResponsible as AccessRuleRoleResponsible,
    GroupResponsible as AccessRuleGroupResponsible,
)


@dataclass(frozen=True, eq=False)
class AccessRule:
    responsible: AccessRuleResponsible
    action: ProjectUnitAction
    is_allow: bool
    order: int = 0

    def __eq__(self, other: "AccessRule") -> bool:
        return self.responsible == other.responsible and self.action == other.action

    def __hash__(self) -> int:
        return hash((self.responsible, self.action))


@dataclass
class ResolvedUnitPermissions:
    allowed: set[ProjectUnitAction] = field(default_factory=set)
    denied: set[ProjectUnitAction] = field(default_factory=set)


class AccessListId(Uuid4): ...


@dataclass
class AccessList(AggregationRoot[AccessListId]):
    name: FileName
    project: ProjectId
    owner: UserId | None
    rules: list[AccessRule] = field(default_factory=list)
