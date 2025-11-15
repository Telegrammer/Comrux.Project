__all__ = ["SqlAlchemyUserMapper"]

from typing import Type
from dataclasses import dataclass
from sqlalchemy import asc, desc, UnaryExpression

from domain.exceptions import DomainFieldError
from domain.value_objects import Title, PassedDatetime
from domain import Project, ProjectId

from application.ports.gateways.query_params import (
    ProjectListParams,
    SortingOrder,
)
from application.ports.mappers import ProjectMapper
from infrastructure.models import (
    Project as OrmProject,
    SqlAlchemySearchParams,
)


class SqlAlchemyProjectMapper(ProjectMapper[Project, OrmProject]):

    def to_dto(self, entity: Project) -> OrmProject:

        return OrmProject(
            id_=entity.id_,
            title=entity.title,
            description=entity.description,
            created_at=entity.created_at,
        )

    def to_domain(self, dto: OrmProject) -> Project:
        return Project(
            id_=ProjectId(dto.id_.__str__()),
            title=Title(dto.title),
            description=dto.description,
            created_at=PassedDatetime(dto.created_at, dto.created_at),
        )

    def generate_search_params(
        self, params: ProjectListParams, model: Type[OrmProject]
    ) -> SqlAlchemySearchParams:
        orders: list[UnaryExpression] = []
        
        for param in params.sorting:

            if param.field_name not in model.__mapper__.attrs:
                raise DomainFieldError(f"Поле {param.field_name} не найдено")
            
            field = OrmProject.__mapper__.attrs[param.field_name]

            orders.append(
                desc(field) if param.sorting_order == SortingOrder.descending else asc(field)
            )

        return SqlAlchemySearchParams(orders=orders)
