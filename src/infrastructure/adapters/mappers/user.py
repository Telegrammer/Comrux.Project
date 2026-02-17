__all__ = ["SqlAlchemyUserMapper"]

from dateutil.relativedelta import relativedelta
from domain.value_objects import Name, BirthDate
from domain import User, UserId

from application.ports.mappers import ProjectMapper
from infrastructure.models import (
    User as OrmUser,
)


class SqlAlchemyUserMapper(ProjectMapper[User, OrmUser]):

    def to_dto(self, entity: User, old_dto: OrmUser | None = None) -> OrmUser:

        return OrmUser(
            id_=entity.id_,
            name=entity.name,
            bio=entity.bio,
            birthdate=entity.birthdate,
        )

    def to_domain(self, dto: OrmUser) -> User:

        return User(
            id_=UserId(dto.id_.__str__()),
            name=Name(dto.name),
            bio=dto.bio,
            birthdate=BirthDate(
                dto.birthdate,
                dto.birthdate,
                dto.birthdate,
                relativedelta(years=0),
            ),
        )
