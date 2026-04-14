from .base import UsecaseError


class ProjectReleaseNotFoundError(UsecaseError): ...


class ProjectReleaseNotReadyError(UsecaseError): ...
