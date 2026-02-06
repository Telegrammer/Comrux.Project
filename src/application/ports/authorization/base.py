__all__ = ["PermissionContext", "Permission", "AuthorizationResult"]


from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class AuthorizationResult:
    success: bool
    detail: str = ""

@dataclass(frozen=True)
class PermissionContext: ...


class Permission[PC: PermissionContext](ABC):
    @abstractmethod
    def is_satisfied_by(self, context: PC) -> AuthorizationResult: ...
