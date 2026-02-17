__all__ = ["SqlAlchemyProjectMapper"]


from domain.enums import ProjectRole
from domain.value_objects import Title, PassedDatetime
from domain import Project, ProjectId, UserId

from application.ports.mappers import ProjectMapper
from application.ports import Clock
from infrastructure.models import (
    Project as OrmProject,
    ProjectMembership,
)


class SqlAlchemyProjectMapper(ProjectMapper[Project, OrmProject]):

    def __init__(self, clock: Clock):
        self._clock: Clock = clock

    def to_dto(self, entity: Project, old_dto: OrmProject | None = None) -> OrmProject:

        version: int = old_dto.version if old_dto else 1
        return OrmProject(
            id_=entity.id_,
            title=entity.title,
            description=entity.description,
            created_at=entity.created_at,
            updated_at=self._clock.now(),
            members=[
                ProjectMembership(
                    project_id=entity.id_, user_id=user_id.value, role=role
                )
                for user_id, role in entity.members.items()
            ],
            version=version,
        )

    def to_domain(self, dto: OrmProject) -> Project:
        members: dict[UserId, ProjectRole] = {}
        for member in dto.members:
            members[UserId(member.user_id.__str__())] = member.role

        return Project(
            id_=ProjectId(dto.id_.__str__()),
            title=Title(dto.title),
            description=dto.description,
            created_at=PassedDatetime(dto.created_at, dto.created_at),
            members=members,
        )
