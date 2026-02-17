from datetime import datetime

from domain.enums import ProjectUnitType
from domain.value_objects import FileName, PassedDatetime
from domain.ports import ProjectUnitVisitor
from domain.entities import Document, DocumentId, DirectoryId, UserId, ProjectId
from domain.entities.document import ContentId
from application.ports.mappers import DocumentMapper, MappingError
from application.ports import Clock
from infrastructure.models import ProjectUnitNode, DocumentAttributes


class SqlAlchemyDocumentMapper(DocumentMapper[ProjectUnitNode]):

    def __init__(self, clock: Clock, unit_visitor: ProjectUnitVisitor):
        self._unit_visitor: ProjectUnitVisitor = unit_visitor
        self._clock: Clock = clock

    def to_domain(self, dto: ProjectUnitNode) -> Document:
        now: datetime = self._clock.now()
        if dto.unit_type != ProjectUnitType.DOCUMENT:
            raise MappingError("Given project unit is not a directory")

        return Document(
            id_=DocumentId(dto.id_.__str__()),
            name=FileName(dto.name),
            project=ProjectId(dto.project_id.__str__()),
            created_by=UserId(dto.created_by.__str__()) if dto.created_by else None,
            created_at=PassedDatetime(dto.created_at, now),
            parent=DirectoryId(dto.parent_id.__str__()),
            content_ref=ContentId(dto.attributes.get("content_ref")),
        )

    def to_dto(self, entity: Document, old_dto: ProjectUnitNode = None):

        attributes: DocumentAttributes = self._unit_visitor.visit_document(entity)
        return ProjectUnitNode(
            id_=entity.id_,
            name=entity.name.value,
            project_id=entity.project,
            created_by=entity.created_by.value,
            created_at=entity.created_at.value,
            parent_id=entity.parent,
            unit_type=entity.unit_type,
            attributes=attributes,
        )
