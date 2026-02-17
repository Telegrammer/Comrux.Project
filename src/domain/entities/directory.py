from __future__ import annotations
from typing import TYPE_CHECKING
from dataclasses import dataclass

from .project_unit import ProjectUnit, ProjectUnitId
from ..enums import ProjectUnitType


if TYPE_CHECKING:
    from ..ports import ProjectUnitVisitor


class DirectoryId(ProjectUnitId): ...


@dataclass(kw_only=True)
class Directory(ProjectUnit):
    parent: DirectoryId | None

    @property
    def unit_type(self) -> ProjectUnitType:
        return ProjectUnitType.DIRECTORY

    def accept[resT](self, visitor: "ProjectUnitVisitor") -> resT:
        return visitor.visit_directory(self)
