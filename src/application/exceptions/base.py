__all__ = [
    "ApplicationError",
    "UsecaseError",
]


class ApplicationError(Exception): ...


class UsecaseError(ApplicationError): ...
