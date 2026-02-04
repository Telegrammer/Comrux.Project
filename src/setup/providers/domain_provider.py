__all__ = ["DomainProvider"]


from datetime import timedelta, date
from dateutil.relativedelta import relativedelta
from dishka import Provider, provide, Scope, from_context
from setup.config import Settings


from domain import ProjectService, UserService
from domain.policies import BirthDatePolicy
from domain.ports import (
    ProjectIdGenerator,
    UserIdGenerator,
)
from infrastructure.adapters import (
    Uuid4ProjectIdGenerator,
    Uuid4UserIdGenerator,
)


class DomainProvider(Provider):
    scope = Scope.REQUEST

    settings = from_context(Settings, scope=Scope.APP)

    project_id_generator = provide(
        source=Uuid4ProjectIdGenerator, provides=ProjectIdGenerator
    )
    project_service = provide(ProjectService)
    user_id_generator = provide(source=Uuid4UserIdGenerator, provides=UserIdGenerator)

    @provide
    def provide_birthdate_policy(self) -> BirthDatePolicy:
        return BirthDatePolicy(
            date(1900, 1, 1), relativedelta(years=18)
        )
    user_service = provide(UserService)
