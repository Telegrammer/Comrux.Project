from typing import Sequence
from domain.ports import ProjectUnitVisitor
from domain.entities import Directory, Document, ProjectUnit


from infrastructure.models import DirectoryAttributes, DocumentAttributes


class JsonProjectUnitVisitor(ProjectUnitVisitor):

    def __init__(self):
        self._saved_units: list[DirectoryAttributes | DocumentAttributes] = []

    def visit_directory(self, directory: Directory) -> DirectoryAttributes:
        return DirectoryAttributes()

    def visit_document(self, document: Document) -> DocumentAttributes:
        print(document)
        return DocumentAttributes(content_ref=document.content_ref)

    def visit_sequence(self, units: Sequence[ProjectUnit]):
        for unit in units:
            self._saved_units.append(unit.accept(self))

    def get_visited(self) -> list[DirectoryAttributes | DocumentAttributes]:
        return self._saved_units.copy()

    def count_visited(self) -> int:
        return len(self._saved_units)
