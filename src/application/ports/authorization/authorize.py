from application.exceptions.authorization import AccessDeniedError
from .base import (
    Permission,
    PermissionContext,
)


def authorize[PC: PermissionContext](
    permission: Permission[PC],
    *,
    context: PC,

) -> None:
    """:raises AuthorizationError:"""
    if not permission.is_satisfied_by(context):
        raise AccessDeniedError()