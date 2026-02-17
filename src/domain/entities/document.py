from dataclasses import dataclass

from .project_unit import ProjectUnit, ProjectUnitId
from .directory import DirectoryId
from ..value_objects import Uuid4
from ..ports import ProjectUnitVisitor
from ..enums import ProjectUnitType


class DocumentId(ProjectUnitId): ...


class ContentId(Uuid4): ...


@dataclass(kw_only=True)
class Document(ProjectUnit):
    parent: DirectoryId
    content_ref: ContentId

    @property
    def unit_type(self) -> ProjectUnitType:
        return ProjectUnitType.DOCUMENT

    def accept[resT](self, visitor: ProjectUnitVisitor) -> resT:
        return visitor.visit_document(self)
