__all__ = ["ApplicationProvider"]


from dishka import Provider, provide, Scope, from_context
from functools import partial
from typing import Callable
from setup.config import Settings


from application.compositions import (
    CreateProjectComposition,
)
from application.usecases import (
    CreateProjectUsecase,
    ListProjectsUsecase,
)
from application.ports import Clock
from application.ports.gateways import (
    ProjectCommandGateway,
    ProjectQueryGateway,
)
from infrastructure.adapters import TimestampClock
from infrastructure.adapters.mappers import (
    SqlAlchemyProjectMapper,
)
from infrastructure.adapters.gateways import (
    SqlAlchemyProjectCommandGateway,
    SqlAlchemyProjectQueryGateway,
)


class ApplicationProvider(Provider):
    scope = Scope.REQUEST
    settings = from_context(Settings, scope=Scope.APP)

    clock = provide(source=TimestampClock, provides=Clock)

    project_mapper = provide(SqlAlchemyProjectMapper)

    project_command_gateway = provide(
        source=SqlAlchemyProjectCommandGateway, provides=ProjectCommandGateway
    )

    project_query_gateway = provide(
        source=SqlAlchemyProjectQueryGateway, provides=ProjectQueryGateway,
    )

    create_project_usecase = provide(CreateProjectUsecase)
    create_project_composition = provide(CreateProjectComposition)
    list_projects_usecase = provide(ListProjectsUsecase)
