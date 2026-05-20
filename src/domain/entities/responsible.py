from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Protocol

from .project_group import ProjectGroupId
from .user import UserId
from ..enums import ProjectRole


class ResponsibleVisitor(Protocol):
    def visit_user[T](self, responsible: "UserResponsible") -> T: ...
    def visit_role[T](self, responsible: "RoleResponsible") -> T: ...
    def visit_group[T](self, responsible: "GroupResponsible") -> T: ...


@dataclass(frozen=True)
class Responsible(ABC):
    @abstractmethod
    def accept[T](self, visitor: ResponsibleVisitor) -> T:
        raise NotImplementedError


@dataclass(init=False, frozen=True, eq=False)
class UserResponsible(Responsible):
    def __init__(self, user_id: str):
        object.__setattr__(self, "user_id", UserId(user_id))
        super().__init__()

    def accept[T](self, visitor: ResponsibleVisitor) -> T:
        return visitor.visit_user(self)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UserResponsible):
            return NotImplemented
        return self.user_id == other.user_id

    def __hash__(self) -> int:
        return hash(self.user_id)


@dataclass(frozen=True)
class RoleResponsible(Responsible):
    role: ProjectRole

    def accept[T](self, visitor: ResponsibleVisitor) -> T:
        return visitor.visit_role(self)


@dataclass(frozen=True, eq=False)
class GroupResponsible(Responsible):
    group_id: ProjectGroupId

    def accept[T](self, visitor: ResponsibleVisitor) -> T:
        return visitor.visit_group(self)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, GroupResponsible):
            return NotImplemented
        return self.group_id == other.group_id

    def __hash__(self) -> int:
        return hash(self.group_id)
