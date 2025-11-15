__all__ = [
    "ProjectAlreadyExistsError",
    "ProjectNotFoundError",
]


from .base import UsecaseError


class ProjectAlreadyExistsError(UsecaseError): ...


class ProjectNotFoundError(UsecaseError): ...
