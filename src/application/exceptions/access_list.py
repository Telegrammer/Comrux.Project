from .base import UsecaseError, ApplicationError


class AccessListAlreadyExistsError(UsecaseError): ...


class AccessListNotFoundError(UsecaseError): ...
