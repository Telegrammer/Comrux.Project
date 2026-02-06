from .base import Permission, PermissionContext, AuthorizationResult


class AnyOf[PC: PermissionContext](Permission[PC]):
    def __init__(self, *permissions: Permission[PC]) -> None:
        self._permissions = permissions

    def is_satisfied_by(self, context: PC) -> AuthorizationResult:
        success: bool = any(
            p.is_satisfied_by(context).success for p in self._permissions
        )
        return (
            AuthorizationResult(True)
            if success
            else AuthorizationResult(False, "None of the permissions are satisfied")
        )


class AllOf[PC: PermissionContext](Permission[PC]):
    def __init__(self, *permissions: Permission[PC]) -> None:
        self._permissions = permissions


    def is_satisfied_by(self, context: PC) -> AuthorizationResult:
        for p in self._permissions:
            result: AuthorizationResult = p.is_satisfied_by(context)
            if not result.success:
                return result
        return AuthorizationResult(True)
