from domain.enums import ProjectUnitType
from typing import Literal
from pydantic import BaseModel, UUID4
from .document import DocumentRead


class DirectoryCreate(BaseModel):
    name: str
    parent_id: UUID4


class DirectoryCreated(BaseModel):
    id_: str


class DirectoryRead(DirectoryCreated):
    unit_type: Literal[ProjectUnitType.DIRECTORY]
    name: str
    owner_name: str | None
    created_by: UUID4 | None


class DirectoryContentRead(BaseModel):
    cursor: str
    data: list[DocumentRead | DirectoryRead]
