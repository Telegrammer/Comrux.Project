__all__ = ["CurrentUserService"]


from domain import User, UserId
from application.ports.gateways import UserQueryGateway
from application.exceptions import CurrentUserNotFoundError


class CurrentUserService:

    def __init__(self, user_id: UserId, gateway: UserQueryGateway):
        self._id: UserId = user_id
        self._gateway: UserQueryGateway = gateway
        self._user: User = None

    async def __call__(self) -> User:
        if self._user:
            return self._user
        self._user = await self._gateway.by_id(self._id.value)
        if not self._user:
            raise CurrentUserNotFoundError("Current user not found")
        return self._user
