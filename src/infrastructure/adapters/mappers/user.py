__all__ = ["SqlAlchemyUserMapper"]

from typing import Type
from dateutil.relativedelta import relativedelta
from dataclasses import dataclass
from sqlalchemy import asc, desc, UnaryExpression

from domain.enums import ProjectRole
from domain.exceptions import DomainFieldError
from domain.value_objects import Name, BirthDate
from domain import User, UserId

from application.ports.gateways.query_params import (
    ProjectListParams,
    SortingOrder,
)
from application.ports.mappers import ProjectMapper
from infrastructure.models import (
    User as OrmUser,
    SqlAlchemySearchParams,
    ProjectMembership,
)


class SqlAlchemyUserMapper(ProjectMapper[User, OrmUser]):

    def to_dto(self, entity: User) -> OrmUser:

        return OrmUser(
            id_=entity.id_,
            name=entity.name,
            bio=entity.bio,
            birthdate=entity.birthdate,
            memberships=[],
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

    def generate_search_params(
        self, params: ProjectListParams, model: Type[OrmUser]
    ) -> SqlAlchemySearchParams:
        orders: list[UnaryExpression] = []

        for param in params.sorting:

            if param.field_name not in model.__mapper__.attrs:
                raise DomainFieldError(f"Поле {param.field_name} не найдено")

            field = model.__mapper__.attrs[param.field_name]

            orders.append(
                desc(field)
                if param.sorting_order == SortingOrder.descending
                else asc(field)
            )

        return SqlAlchemySearchParams(orders=orders)

