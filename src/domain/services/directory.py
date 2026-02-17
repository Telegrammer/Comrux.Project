from datetime import datetime

from domain.ports import ProjectUnitIdGenerator
from domain.entities import Project, UserId, ProjectId, Directory, DirectoryId
from domain.value_objects import FileName, PassedDatetime
from domain.exceptions import MemberNotFoundError, DomainFieldError, DomainError
from domain.enums import ProjectRole


class DirectoryService:

    def __init__(self, id_generator: ProjectUnitIdGenerator):
        self._id_generator: ProjectUnitIdGenerator = id_generator

    def create_directory(
        self,
        project: Project,
        parent: Directory,
        creator: UserId,
        name: FileName,
        now: datetime,
    ) -> Directory:

        if name.value == "":
            raise DomainFieldError("Directory name must not be empty")

        if parent.project.value != project.id_:
            raise DomainFieldError("Parent directory must be in the same project")

        if not project.members.get(creator):
            raise MemberNotFoundError("Only members of the project could add documents")

        return Directory(
            id_=self._id_generator(),
            name=name,
            parent=parent.id_,
            project=ProjectId(project.id_),
            created_by=creator,
            created_at=PassedDatetime(now, now),
        )

    def create_root_directory(
        self,
        project: Project,
        owner: UserId,
        now: datetime,
    ) -> Directory:
        role = project.members.get(owner)

        if not role or role != ProjectRole.OWNER:
            raise DomainError("Given user is not owner of this project")

        return Directory(
            id_=self._id_generator(),
            name=FileName(""),
            project=ProjectId(project.id_),
            parent=None,
            created_by=owner,
            created_at=PassedDatetime(now, now),
        )

    def is_root(self, directory: Directory) -> bool:
        return directory.parent is None

    def set_parent(
        self, directory: Directory, parent: Directory, now: datetime
    ) -> Directory:
        if directory.parent is None:
            raise DomainError(
                "Given directory is root directory so he can't have parent"
            )

        if parent.project.value != directory.project:
            raise DomainFieldError("Parent directory must be in the same project")

        if parent.parent.value == directory.id_:
            raise DomainError("Two directories can't link to each other")

        if directory.parent.value == parent.id_:
            return directory

        return Directory(
            id_=DirectoryId(directory.id_),
            title=directory.name,
            project=directory.project,
            parent=DirectoryId(parent.id_),
            created_by=directory.created_by,
            created_at=PassedDatetime(directory.created_at.value, now),
        )
