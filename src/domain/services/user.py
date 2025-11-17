__all__ = ["UserService"]


from datetime import date
from dateutil.relativedelta import relativedelta

from ..policies import BirthDatePolicy
from ..entities import Project, User
from ..value_objects import Name, BirthDate
from ..ports import UserIdGenerator


class UserService:

    def __init__(
        self, birthdate_policy: BirthDatePolicy, id_generator: UserIdGenerator
    ):
        self._birthdate_policy: BirthDatePolicy = birthdate_policy
        self._id_generator: UserIdGenerator = id_generator

    def create_user(
        self, now: date, name: Name, bio: str, birthdate: date, projects: list[Project]
    ):
        verified_birthdate: BirthDate = BirthDate(
            birthdate,
            self._birthdate_policy.low_border,
            now,
            self._birthdate_policy.age_border,
        )
        return User(
            id_=self._id_generator(),
            name=name,
            bio=bio,
            birthdate=verified_birthdate,
            projects=projects,
        )
