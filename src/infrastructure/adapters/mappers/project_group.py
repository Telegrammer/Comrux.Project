from domain.entities import (
    ProjectGroup,
    ProjectGroupId,
    ProjectId,
    UserId,
)
from domain.value_objects import HexColor, Title

from infrastructure.models import (
    ProjectGroup as OrmProjectGroup,
    ProjectGroupParticipant,
)


class SqlAlchemyProjectGroupMapper:
    def to_dto(self, entity: ProjectGroup) -> OrmProjectGroup:
        return OrmProjectGroup(
            id_=entity.id_,
            project_id=entity.project_id,
            owner_id=entity.owner,
            name=entity.name,
            color=entity.color,
            is_public=entity.is_public,
            participants=[
                ProjectGroupParticipant(group_id=entity.id_, user_id=user_id.value)
                for user_id in entity.participants
            ],
        )

    def to_domain(self, dto: OrmProjectGroup) -> ProjectGroup:
        return ProjectGroup(
            id_=ProjectGroupId(str(dto.id_)),
            project_id=ProjectId(str(dto.project_id)),
            owner=UserId(str(dto.owner_id)),
            name=Title(dto.name),
            color=HexColor(dto.color),
            is_public=dto.is_public,
            participants=[UserId(str(item.user_id)) for item in dto.participants],
        )
