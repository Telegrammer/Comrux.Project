__all__ = ["CreateUserRequest", "CreateUserResponse", "CreateUserUsecase"]


from typing import TypedDict
from datetime import date
from dataclasses import dataclass

from domain import User, UserId
from domain.services import UserService
from domain.value_objects import Name, BirthDate, EmailAddress
from application.ports import UserCommandGateway, Clock


@dataclass
class CreateUserRequest:

    name: Name
    bio: str
    email: EmailAddress
    birthdate: date

    @classmethod
    def from_primitives(
        cls, *, name: str, email: str, bio: str, birthdate: date
    ) -> "CreateUserRequest":
        return cls(name=Name(name), email=EmailAddress(email), bio=bio, birthdate=birthdate)


class CreateUserUsecase:

    def __init__(
        self, clock: Clock, user_service: UserService, user_gateway: UserCommandGateway
    ):
        self._user_service: UserService = user_service
        self._user_gateway: UserCommandGateway = user_gateway
        self._clock: Clock = clock

    async def __call__(self, request: CreateUserRequest) -> None:
        now: date = self._clock.now().date()
        new_user: User = self._user_service.create_user(
            now, request.email, request.name, request.bio, request.birthdate
        )
        await self._user_gateway.add(new_user)
        return CreateUserResponse.from_entity(new_user)


class CreateUserResponse(TypedDict):

    user_id: UserId

    @classmethod
    def from_entity(cls, user: User) -> "CreateUserResponse":
        return cls(user_id=user.id_)
