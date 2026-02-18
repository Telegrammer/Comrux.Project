from datetime import datetime

from domain.enums import ProjectUnitType
from domain.value_objects import FileName, PassedDatetime
from domain.ports import ProjectUnitVisitor
from domain.entities import Directory, DirectoryId, UserId, ProjectId
from application.exceptions import DirectoryNotFoundError
from application.ports.mappers import DirectoryMapper
from application.ports import Clock
from infrastructure.models import (
    ProjectUnitNode,
    DirectoryAttributes,
)


class SqlAlchemyDirectoryMapper(DirectoryMapper[ProjectUnitNode]):

    def __init__(self, clock: Clock, unit_visitor: ProjectUnitVisitor):
        self._unit_visitor: ProjectUnitVisitor = unit_visitor
        self._clock: Clock = clock

    def to_domain(self, dto: ProjectUnitNode) -> Directory:
        now: datetime = self._clock.now()
        if dto.unit_type != ProjectUnitType.DIRECTORY:
            raise DirectoryNotFoundError("Given project unit is not a directory")

        return Directory(
            id_=DirectoryId(dto.id_.__str__()),
            name=FileName(dto.name),
            project=ProjectId(dto.project_id.__str__()),
            created_by=UserId(str(dto.created_by)) if dto.created_by else None,
            created_at=PassedDatetime(dto.created_at, now),
            parent=DirectoryId(str(dto.parent_id)) if dto.parent_id else None,
        )

    def to_dto(self, entity: Directory, old_dto: ProjectUnitNode = None):

        attributes: DirectoryAttributes = self._unit_visitor.visit_directory(entity)
        return ProjectUnitNode(
            id_=entity.id_,
            name=entity.name.value,
            project_id=entity.project.value,
            created_by=entity.created_by.value,
            created_at=entity.created_at.value,
            parent_id=entity.parent,
            unit_type=entity.unit_type,
            attributes=attributes,
        )
