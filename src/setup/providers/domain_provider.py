__all__ = ["DomainProvider"]


from datetime import timedelta
from dishka import Provider, provide, Scope, from_context
from setup.config import Settings


from domain import ProjectService
from domain.ports import ProjectIdGenerator
from infrastructure.adapters import Uuid4ProjectIdGenerator


class DomainProvider(Provider):
    scope = Scope.REQUEST

    settings = from_context(Settings, scope=Scope.APP)

    project_id_generator = provide(
        source=Uuid4ProjectIdGenerator, provides=ProjectIdGenerator
    )
    project_service = provide(ProjectService)
