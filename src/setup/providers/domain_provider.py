__all__ = ["DomainProvider"]


from datetime import timedelta, date
from dateutil.relativedelta import relativedelta
from dishka import Provider, provide, Scope, from_context
from setup.config import Settings


from domain import ProjectService, UserService, DirectoryService, DocumentService
from domain.policies import BirthDatePolicy
from domain.ports import (
    ProjectIdGenerator,
    UserIdGenerator,
    ProjectUnitIdGenerator,
    ProjectUnitVisitor,
    ContentIdGenerator,
)
from infrastructure.adapters import (
    Uuid4ProjectIdGenerator,
    Uuid4UserIdGenerator,
    Uuid4ProjectUnitIdGenerator,
    Uuid4ContentIdGenerator,
    JsonProjectUnitVisitor,
)


class DomainProvider(Provider):
    scope = Scope.REQUEST

    settings = from_context(Settings, scope=Scope.APP)

    project_id_generator = provide(
        source=Uuid4ProjectIdGenerator, provides=ProjectIdGenerator
    )
    project_service = provide(ProjectService)
    user_id_generator = provide(source=Uuid4UserIdGenerator, provides=UserIdGenerator)
    project_unit_id_generator = provide(
        source=Uuid4ProjectUnitIdGenerator, provides=ProjectUnitIdGenerator
    )
    content_id_generator = provide(
        source=Uuid4ContentIdGenerator, provides=ContentIdGenerator
    )
    project_unit_visitor = provide(
        source=JsonProjectUnitVisitor, provides=ProjectUnitVisitor
    )

    @provide
    def provide_birthdate_policy(self) -> BirthDatePolicy:
        return BirthDatePolicy(date(1900, 1, 1), relativedelta(years=12))

    user_service = provide(UserService)
    directory_service = provide(DirectoryService)
    document_service = provide(DocumentService)
