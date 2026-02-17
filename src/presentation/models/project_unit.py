from pydantic import BaseModel, UUID4

from domain.enums import ProjectUnitType
from .document import DocumentRead
from .directory import DirectoryRead


class ProjectUnitCreate(BaseModel):
    name: str
    unit_type: ProjectUnitType
    parent_id: UUID4


ProjectUnitRead = DirectoryRead | DocumentRead
