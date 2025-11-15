__all__ = ["UserMapper", "AccessKeyMapper", "EmailVerififcationMapper"]

from abc import ABC, abstractmethod


from domain import Entity, Project


class DataMapper[TEntity: Entity, Tdto](ABC):

    @abstractmethod
    def to_dto(
        self,
        entity: TEntity,
    ) -> Tdto:
        raise NotImplementedError

    @abstractmethod
    def to_domain(self, dto: Tdto) -> TEntity:
        raise NotImplementedError

    @abstractmethod
    def generate_search_params[TSearch, TResult](
        self, params: TSearch, model: Tdto
    ) -> TResult:
        raise NotImplementedError


class ProjectMapper[Project, Tdto](DataMapper): ...
