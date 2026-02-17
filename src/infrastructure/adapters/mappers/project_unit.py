from functools import singledispatchmethod

from domain.entities import Document, Directory, ProjectUnit
from infrastructure.models.project_unit_node import (
    ProjectUnitNode,
    DirectoryNode,
    DocumentNode,
)
from .document import SqlAlchemyDocumentMapper
from .directory import SqlAlchemyDirectoryMapper


class ProjectUnitNodeMapper:

    def __init__(
        self,
        directory_mapper: SqlAlchemyDirectoryMapper,
        document_mapper: SqlAlchemyDocumentMapper,
    ):
        self._directory_mapper = directory_mapper
        self._document_mapper = document_mapper

    @singledispatchmethod
    def to_domain(self, node: ProjectUnitNode) -> ProjectUnit:
        raise NotImplementedError("Unknown node type")

    @to_domain.register
    def _(self, node: DirectoryNode) -> Directory:
        return self._directory_mapper.to_domain(node)

    @to_domain.register
    def _(self, node: DocumentNode) -> Document:
        return self._document_mapper.to_domain(node)