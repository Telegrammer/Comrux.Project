from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Protocol

from domain.entities.access_list import (
    AccessRuleTarget,
    AccessRuleGroupTarget,
    AccessRuleRoleTarget,
    AccessRuleUserTarget,
)

class AccessRuleTargetResolutionOrder(Protocol):
    """Iteration order: first target class is applied first."""

    def __iter__(self) -> Iterator[type[AccessRuleTarget]]: ...


DEFAULT_ACCESS_RULE_TARGET_ORDER: tuple[type[AccessRuleTarget], ...] = (
    AccessRuleUserTarget,
    AccessRuleGroupTarget,
    AccessRuleRoleTarget,
)


@dataclass(frozen=True)
class FixedAccessRuleTargetResolutionOrder:
    kinds: tuple[type[AccessRuleTarget], ...] = DEFAULT_ACCESS_RULE_TARGET_ORDER

    def __iter__(self) -> Iterator[type[AccessRuleTarget]]:
        return iter(self.kinds)
