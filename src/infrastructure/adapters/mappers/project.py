__all__ = ["SqlAlchemyProjectMapper"]


from dataclasses import dataclass
from domain.enums import ProjectRole
from domain.value_objects import Title, PassedDatetime
from domain import Project, ProjectId, UserId, DirectoryId


from application.ports.mappers import ProjectMapper
from application.ports import Clock
from infrastructure.models import (
    Project as OrmProject,
    ProjectMembership,
    ProjectDto,
)


class SqlAlchemyProjectMapper(ProjectMapper[ProjectDto]):
    def __init__(self, clock: Clock):
        self._clock: Clock = clock

    def to_dto(self, entity: Project, old_dto: ProjectDto | None = None) -> ProjectDto:

        version: int = old_dto.version if old_dto else 1
        return ProjectDto(
            OrmProject(
                id_=entity.id_,
                title=entity.title,
                description=entity.description,
                created_at=entity.created_at,
                updated_at=self._clock.now(),
                is_private=entity.is_private,
                members=[
                    ProjectMembership(
                        project_id=entity.id_, user_id=user_id.value, role=role
                    )
                    for user_id, role in entity.members.items()
                ],
                version=version,
            ),
            None,
        )

    def to_domain(self, dto: ProjectDto) -> Project:
        members: dict[UserId, ProjectRole] = {}
        for member in dto.orm_model.members:
            members[UserId(member.user_id.__str__())] = member.role

        return Project(
            id_=ProjectId(dto.orm_model.id_.__str__()),
            title=Title(dto.orm_model.title),
            root_directory=DirectoryId(dto.root_directory.__str__()),
            description=dto.orm_model.description,
            is_private=dto.orm_model.is_private,
            created_at=PassedDatetime(
                dto.orm_model.created_at, dto.orm_model.created_at
            ),
            members=members,
        )
