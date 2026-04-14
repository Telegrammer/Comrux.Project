from dishka import Provider, Scope, from_context, provide

from application.export import (
    BuildProjectReleaseComposition,
    CreateProjectReleaseComposition,
    CreateProjectReleaseUsecase,
    DownloadProjectReleaseUsecase,
    GetProjectReleaseUsecase,
    GroupPublishedContentGateway,
    ProjectReleaseArtifactGateway,
    ProjectReleaseCommandGateway,
    ProjectReleaseQueryGateway,
    ProjectTreeSnapshotGateway,
)
from infrastructure.export import (
    HttpGroupPublishedContentGateway,
    S3ProjectReleaseArtifactGateway,
    SqlAlchemyProjectReleaseCommandGateway,
    SqlAlchemyProjectReleaseQueryGateway,
    SqlAlchemyProjectTreeSnapshotGateway,
)
from setup.config import Settings


class ExportApplicationProvider(Provider):
    scope = Scope.REQUEST

    settings = from_context(Settings, scope=Scope.APP)

    release_command_gateway = provide(
        source=SqlAlchemyProjectReleaseCommandGateway,
        provides=ProjectReleaseCommandGateway,
    )
    release_query_gateway = provide(
        source=SqlAlchemyProjectReleaseQueryGateway,
        provides=ProjectReleaseQueryGateway,
    )
    tree_snapshot_gateway = provide(
        source=SqlAlchemyProjectTreeSnapshotGateway,
        provides=ProjectTreeSnapshotGateway,
    )
    group_published_content_gateway = provide(
        source=HttpGroupPublishedContentGateway,
        provides=GroupPublishedContentGateway,
    )
    artifact_gateway = provide(
        source=S3ProjectReleaseArtifactGateway,
        provides=ProjectReleaseArtifactGateway,
    )

    create_project_release_usecase = provide(CreateProjectReleaseUsecase)
    get_project_release_usecase = provide(GetProjectReleaseUsecase)
    download_project_release_usecase = provide(DownloadProjectReleaseUsecase)

    create_project_release_composition = provide(CreateProjectReleaseComposition)
    build_project_release_composition = provide(BuildProjectReleaseComposition)
