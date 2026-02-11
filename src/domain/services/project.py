from datetime import datetime

from domain.value_objects import Title, PassedDatetime
from domain.entities import Project, ProjectId, UserId
from domain.ports import ProjectIdGenerator
from domain.enums import ProjectRole
from domain.exceptions import ProjectMustHaveOwnerError, MemberNotFoundError


class ProjectService:

    def __init__(self, id_generator: ProjectIdGenerator):
        self._id_generator = id_generator

    def create_project(
        self, title: Title, description: str, now: datetime, owner: UserId
    ) -> Project:
        return Project(
            id_=self._id_generator(),
            title=title,
            description=description,
            created_at=PassedDatetime(now, now),
            members={UserId(owner): ProjectRole.OWNER},
        )

    def update_project(
        self, project: Project, title: Title, description: str, now: datetime
    ) -> Project:
        return Project(
            id_=ProjectId(project.id_),
            title=title,
            description=description,
            created_at=PassedDatetime(project.created_at, now),
            members=project.members,
        )

    def add_member(self, project: Project, member: UserId, now: datetime) -> Project:

        project.members[UserId(member)] = ProjectRole.MEMBER

        return Project(
            id_=ProjectId(project.id_),
            title=Title(project.title),
            description=project.description,
            created_at=PassedDatetime(project.created_at, now),
            members=project.members,
        )

    def remove_member(
        self, project: Project, removed_member: UserId, now: datetime
    ) -> Project:
        if not project.members.get(removed_member, None):
            return project

        if self.get_owner_id(project) == removed_member:
            raise ProjectMustHaveOwnerError("Every project must have owner")

        project.members.pop(removed_member)
        return Project(
            id_=ProjectId(project.id_),
            title=Title(project.title),
            description=project.description,
            created_at=PassedDatetime(project.created_at, now),
            members=project.members,
        )

    def get_owner_id(self, project: Project) -> UserId:

        for user_id in project.members.keys():
            if project.members.get(user_id) == ProjectRole.OWNER:
                return user_id
        raise ProjectMustHaveOwnerError("Project doesen't have owner")

    def grant_owner(
        self, project: Project, new_owner: UserId, now: datetime
    ) -> Project:
        if not project.members.get(new_owner):
            raise MemberNotFoundError(
                f"New owner {new_owner.value} doesen't belong to project {project.id_}"
            )
        owner_id: UserId = self.get_owner_id(project)
        new_members: dict[UserId, ProjectRole] = project.members.copy()
        new_members[owner_id] = ProjectRole.LEAD
        new_members[new_owner] = ProjectRole.OWNER
        return Project(
            id_=ProjectId(project.id_),
            title=Title(project.title),
            description=project.description,
            created_at=PassedDatetime(project.created_at, now),
            members=new_members,
        )

    def set_role(
        self, project: Project, member: UserId, new_role: ProjectRole, now: datetime
    ) -> Project:

        new_members: dict[UserId, ProjectRole] = project.members.copy()
        new_members[member] = new_role

        return Project(
            id_=ProjectId(project.id_),
            title=Title(project.title),
            description=project.description,
            created_at=PassedDatetime(project.created_at, now),
            members=new_members,
        )
