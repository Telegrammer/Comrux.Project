from typing import Literal
from domain.enums import ProjectUnitType
from pydantic import BaseModel, UUID4


class DocumentCreate(BaseModel):
    name: str
    parent_id: UUID4


class DocumentCreated(BaseModel):
    id_: str
    content_ref: str


class DocumentRead(DocumentCreated):
    unit_type: Literal[ProjectUnitType.DOCUMENT]
    name: str
    created_by: UUID4
