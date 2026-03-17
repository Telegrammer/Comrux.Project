from typing import TypedDict
from dataclasses import dataclass
from domain.entities import User, UserId

from domain.value_objects import Name, BirthDate
from application.ports import UserQueryGateway


@dataclass
class GetUserRequest:

    user_id: UserId

    @classmethod
    def from_primitives(cls, user_id: str) -> "GetUserRequest":
        return cls(user_id=UserId(user_id))


class GetUserResponse(TypedDict):

    name: Name
    bio: str
    birthdate: BirthDate

    @classmethod
    def from_entity(cls, user: User) -> "GetUserResponse":
        return cls(
            name=user.name,
            bio=user.bio,
            birthdate=user.birthdate,
        )


class GetUserUsecase:

    def __init__(self, user_gateway: UserQueryGateway):
        self._user_gateway = user_gateway

    async def __call__(self, request: GetUserRequest):
        found_user: User = await self._user_gateway.by_id(request.user_id.value)
        return GetUserResponse.from_entity(found_user)
