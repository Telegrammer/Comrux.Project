__all__ = ["CurrentUserService"]


from domain import User, UserId
from application.ports.gateways import UserQueryGateway
from application.exceptions.user import (
    CurrentUserNotFoundError,
    CurrentUserNotAssignError,
)


class CurrentUserService:
    def __init__(self, user_id: UserId | None, gateway: UserQueryGateway):
        self._id: UserId | None = user_id
        self._gateway: UserQueryGateway = gateway
        self._user: User = None

    async def __call__(self) -> User:
        if not self._id:
            raise CurrentUserNotAssignError("Current user is not assigned")
        if self._user:
            return self._user
        self._user = await self._gateway.by_id(self._id.value)
        if not self._user:
            raise CurrentUserNotFoundError("Current user not found")
        return self._user
