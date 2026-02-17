from .base import UsecaseError


class DirectoryAlreadyExistsError(UsecaseError): ...


class DirectoryNotFoundError(UsecaseError): ...


class DirectoryNotInProjectError(UsecaseError): ...
