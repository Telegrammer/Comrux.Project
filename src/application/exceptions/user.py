__all__ = [
    "UserAlreadyExistsError",
    "UserNotFoundError",
]


from .base import UsecaseError, ApplicationError


class UserAlreadyExistsError(UsecaseError): ...


class UserNotFoundError(UsecaseError): ...


class CurrentUserNotFoundError(ApplicationError): ...
