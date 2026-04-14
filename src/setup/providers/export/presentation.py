from dishka import Provider, Scope, provide

from presentation.export import (
    CreateProjectReleaseHandler,
    DownloadProjectReleaseHandler,
    GetProjectReleaseHandler,
)


class ExportPresentationProvider(Provider):
    scope = Scope.REQUEST

    create_project_release_handler = provide(CreateProjectReleaseHandler)
    get_project_release_handler = provide(GetProjectReleaseHandler)
    download_project_release_handler = provide(DownloadProjectReleaseHandler)
