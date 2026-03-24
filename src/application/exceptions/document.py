from .base import UsecaseError
from .project_unit import UnitNotInProjectError


class DocumentAlreadyExistsError(UsecaseError): ...


class DocumentNotFoundError(UsecaseError): ...


class DocumentNotInProjectError(UnitNotInProjectError): ...
