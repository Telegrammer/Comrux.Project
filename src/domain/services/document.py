from datetime import datetime

from domain.ports import ProjectUnitIdGenerator, ContentIdGenerator
from domain.entities import Project, UserId, Document, ProjectId, Directory, DirectoryId
from domain.value_objects import FileName, PassedDatetime
from domain.exceptions import MemberNotFoundError, DomainFieldError


class DocumentService:

    def __init__(
        self,
        id_generator: ProjectUnitIdGenerator,
        content_id_generator: ContentIdGenerator,
    ):
        self._id_generator: ProjectUnitIdGenerator = id_generator
        self._content_id_generator: ContentIdGenerator = content_id_generator

    def create_document(
        self,
        project: Project,
        parent: Directory,
        creator: UserId,
        name: FileName,
        now: datetime,
    ) -> Document:

        if name.value == "":
            raise DomainFieldError("Document name must not be empty")

        if parent.project.value != project.id_:
            raise DomainFieldError("Parent directory must be in the same project")

        if not project.members.get(creator):
            raise MemberNotFoundError("Only members of the project could add documents")

        return Document(
            id_=self._id_generator(),
            name=name,
            parent=DirectoryId(parent.id_),
            project=project.id_,
            content_ref=self._content_id_generator(),
            created_by=creator,
            created_at=PassedDatetime(now, now),
        )

    def belongs_to(self, document: Document, project: Project) -> bool:
        return document.project.value == project.id_
