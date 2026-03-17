from typing import TypedDict, Sequence
from application.ports.gateways.query_params.user import UserListParams
from application.ports.gateways import UserQueryGateway

from domain.entities.user import User, UserId
from domain.value_objects import EmailAddress, BirthDate, Name


class ListUsersElementResponse(TypedDict):

    id_: UserId
    name: Name
    email: EmailAddress
    bio: str

    @classmethod
    def from_entity(cls, user: User) -> "ListUsersElementResponse":
        return cls(
            id_=user.id_,
            name=user.name,
            email=user.email,
            bio=user.bio,
        )


class ListUsersUsecase:

    def __init__(self, user_gateway: UserQueryGateway):
        self._user_gateway = user_gateway

    async def __call__(
        self, search_params: UserListParams
    ) -> list[ListUsersElementResponse]:

        found_users: Sequence[User] = await self._user_gateway.read_all(search_params)
        return [ListUsersElementResponse.from_entity(user) for user in found_users]
