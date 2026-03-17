from typing import Sequence
from pydantic import UUID4

from domain.entities import Document, Directory, ProjectUnit, UserId, User
from domain.ports import ProjectUnitVisitor
from presentation.models import DocumentRead, DirectoryRead


class PydanticProjectUnitVisitor(ProjectUnitVisitor):

    def __init__(self):
        self._units: list[DocumentRead | DirectoryRead] = []
        self._owners: dict[UserId, User] = {}

    def visit_document(self, document: Document) -> DocumentRead:

        return DocumentRead(
            id_=document.id_,
            content_ref=document.content_ref,
            unit_type=document.unit_type,
            name=document.name.value,
            owner_name=self._owners[UserId(document.created_by.value)].name,
            created_by=UUID4(document.created_by.value),
        )

    def visit_directory(self, directory: Directory) -> DirectoryRead:
        return DirectoryRead(
            id_=directory.id_,
            unit_type=directory.unit_type,
            name=directory.name.value,
            owner_name=self._owners[UserId(directory.created_by.value)].name,
            created_by=UUID4(directory.created_by.value),
        )

    def visit_sequence(
        self, units: Sequence[ProjectUnit], owners: dict[UserId, User] = {}
    ) -> None:
        self._units = []
        self._owners = owners
        self._units: list[DirectoryRead | DocumentRead] = [
            unit.accept(self) for unit in units
        ]

    def get_visited(self) -> list[DirectoryRead, DocumentRead]:
        return self._units

    def count_visited(self) -> int:
        return len(self._units)
