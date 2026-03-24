from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from dataclasses import dataclass
from abc import abstractmethod

from .base import Entity
from .project import ProjectId
from .user import UserId
from .access_list import AccessListId
from ..value_objects import Uuid4, FileName, PassedDatetime
from ..enums import ProjectUnitType

if TYPE_CHECKING:
    from domain.ports import ProjectUnitVisitor


class ProjectUnitId(Uuid4): ...


@dataclass(kw_only=True)
class ProjectUnit(Entity[ProjectUnitId]):

    name: FileName
    project: ProjectId
    created_at: PassedDatetime
    access_list: AccessListId | None
    created_by: UserId | None

    @property
    def unit_type(self) -> ProjectUnitType:
        raise NotImplementedError

    def accept[resT](self, vistor: ProjectUnitVisitor) -> resT:
        raise NotImplementedError
