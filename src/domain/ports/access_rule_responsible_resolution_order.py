from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Protocol

from domain.entities.responsible import (
    Responsible,
    UserResponsible,
    GroupResponsible,
    RoleResponsible,
)


class AccessRuleResponsibleResolutionOrder(Protocol):
    """Iteration order: first responsible class is applied first."""

    def __iter__(self) -> Iterator[type[Responsible]]: ...


DEFAULT_ACCESS_RULE_RESPONSIBLE_ORDER: tuple[type[Responsible], ...] = (
    UserResponsible,
    GroupResponsible,
    RoleResponsible,
)


@dataclass(frozen=True)
class FixedAccessRuleResponsibleResolutionOrder:
    kinds: tuple[type[Responsible], ...] = DEFAULT_ACCESS_RULE_RESPONSIBLE_ORDER

    def __iter__(self) -> Iterator[type[Responsible]]:
        return iter(self.kinds)
