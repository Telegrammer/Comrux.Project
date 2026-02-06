from application.exceptions.authorization import AccessDeniedError
from .base import Permission, PermissionContext, AuthorizationResult


def authorize[PC: PermissionContext](
    permission: Permission[PC],
    *,
    context: PC,
) -> None:
    """:raises AuthorizationError:"""
    result: AuthorizationResult = permission.is_satisfied_by(context)
    if not result.success:
        raise AccessDeniedError(result.detail)
