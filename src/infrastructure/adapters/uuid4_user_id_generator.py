__all__ = ["Uuid4UserIdGenerator"]


import uuid


from domain.ports import UserIdGenerator
from domain import UserId


class Uuid4UserIdGenerator(UserIdGenerator):

    def __call__(self) -> UserId:
        return UserId(str(uuid.uuid4()))
