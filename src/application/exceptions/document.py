from .base import UsecaseError


class DocumentAlreadyExistsError(UsecaseError): ...


class DocumentNotFoundError(UsecaseError): ...
