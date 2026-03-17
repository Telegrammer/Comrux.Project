from typing import TypedDict


from domain.value_objects import Name, BirthDate
from domain.entities import User
from application.services import CurrentUserService


class GetCurrentUserResponse(TypedDict):

    name: Name
    bio: str
    birthdate: BirthDate

    @classmethod
    def from_entity(cls, current_user: User) -> "GetCurrentUserResponse":
        return cls(
            name=current_user.name,
            bio=current_user.bio,
            birthdate=current_user.birthdate,
        )


class GetCurrentUserUsecase:

    def __init__(self, service: CurrentUserService):
        self._service = service

    async def __call__(self) -> GetCurrentUserResponse:
        return GetCurrentUserResponse.from_entity((await self._service()))
