__all__ = ["ExpiredAccessKeyError", "AccessDeniedError", "CurrentUserNotFound"]


from .base import ApplicationError


class ExpiredAccessKeyError(ApplicationError): ...


class AccessDeniedError(ApplicationError): ...


class CurrentUserNotFoundError(ApplicationError): ...
