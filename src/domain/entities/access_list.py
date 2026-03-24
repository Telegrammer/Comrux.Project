from dataclasses import dataclass, field
from abc import abstractmethod, ABC
from typing import Protocol

from ..enums import ProjectRole, ProjectUnitAction
from ..value_objects import Uuid4, FileName
from .base import AggregationRoot
from .user import UserId
from .project import ProjectId, Project


class AccessRuleTargetVisitor(Protocol):

    def visit_user[T](self, target: "AccessRuleUserTarget") -> T: ...
    def visit_role[T](self, target: "AccessRuleRoleTarget") -> T: ...


@dataclass(frozen=True)
class AccessRuleTarget[valT](ABC):

    @abstractmethod
    def accept[T](self, visitor: AccessRuleTargetVisitor) -> T:
        raise NotImplementedError


@dataclass(init=False, frozen=True, eq=False)
class AccessRuleUserTarget(AccessRuleTarget[UserId]):

    user_id: UserId

    def __init__(self, user_id: str):
        self.user_id = UserId(user_id)

    def accept[T](self, visitor: AccessRuleTargetVisitor) -> T:
        return visitor.visit_user(self)

    def __eq__(self, other):
        return self.user_id == other.user_id

    def __hash__(self):
        return hash(self.user_id)


@dataclass(frozen=True)
class AccessRuleRoleTarget(AccessRuleTarget):

    role: ProjectRole

    def accept[T](self, visitor: AccessRuleTargetVisitor) -> T:
        return visitor.visit_role(self)

    def __eq__(self, other: "AccessRuleRoleTarget") -> bool:
        return self.role == other.role

    def __hash__(self):
        return hash(self.role)


@dataclass(frozen=True, eq=False)
class AccessRule:
    target: AccessRuleTarget
    action: ProjectUnitAction
    is_allow: bool

    def __eq__(self, other: "AccessRule") -> bool:
        return self.target == other.target and self.action == other.action

    def __hash__(self) -> int:
        return hash((self.target, self.action))


@dataclass
class ResolvedUnitPermissions:
    allowed: dict[UserId, ProjectUnitAction] = field(default_factory=set)
    denied: dict[UserId, ProjectUnitAction] = field(default_factory=set)


class AccessListId(Uuid4): ...


@dataclass
class AccessList(AggregationRoot[AccessListId]):

    name: FileName
    project: ProjectId
    owner: UserId | None
    rules: list[AccessRule] = field(default_factory=list)
