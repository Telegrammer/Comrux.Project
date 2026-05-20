from .base import UsecaseError


class ProjectTaskAlreadyExistsError(UsecaseError): ...


class ProjectTaskNotFoundError(UsecaseError): ...


class ProjectTaskNotInProjectError(UsecaseError): ...
