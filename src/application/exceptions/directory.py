from .base import UsecaseError
from .project_unit import UnitNotInProjectError


class DirectoryAlreadyExistsError(UsecaseError): ...


class DirectoryNotFoundError(UsecaseError): ...


class DirectoryNotInProjectError(UnitNotInProjectError): ...
