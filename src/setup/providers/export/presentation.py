from dishka import Provider, Scope, provide

from presentation.export import (
    CreateProjectReleaseHandler,
    DownloadProjectReleaseHandler,
    GetProjectReleaseHandler,
    ListProjectReleasesHandler,
)


class ExportPresentationProvider(Provider):
    scope = Scope.REQUEST

    create_project_release_handler = provide(CreateProjectReleaseHandler)
    get_project_release_handler = provide(GetProjectReleaseHandler)
    list_project_releases_handler = provide(ListProjectReleasesHandler)
    download_project_release_handler = provide(DownloadProjectReleaseHandler)
