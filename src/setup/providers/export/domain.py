from dishka import Provider, Scope, provide

from domain.export import ProjectReleaseService
from domain.export.ports import ProjectReleaseIdGenerator
from infrastructure.export import Uuid4ProjectReleaseIdGenerator


class ExportDomainProvider(Provider):
    scope = Scope.REQUEST

    project_release_id_generator = provide(
        source=Uuid4ProjectReleaseIdGenerator,
        provides=ProjectReleaseIdGenerator,
    )
    project_release_service = provide(ProjectReleaseService)
