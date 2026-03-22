from abc import ABC, abstractmethod


from domain import Entity, Project, User, Directory, Document, ProjectUnit
from domain.entities import Task


class DataMapper[TEntity: Entity, Tdto](ABC):

    @abstractmethod
    def to_dto(self, entity: TEntity, old_dto: Tdto | None = None) -> Tdto:
        raise NotImplementedError

    @abstractmethod
    def to_domain(self, dto: Tdto) -> TEntity:
        raise NotImplementedError


class ProjectMapper[Tdto](DataMapper[Project, Tdto]): ...


class UserMapper[Tdto](DataMapper[User, Tdto]): ...


class ProjectUnitMapper[TEntity: ProjectUnit, Tdto](DataMapper): ...


class DirectoryMapper[Tdto](ProjectUnitMapper[Directory, Tdto]): ...


class DocumentMapper[Tdto](ProjectUnitMapper[Document, Tdto]): ...


class TaskMapper[Tdto](DataMapper[Task, Tdto]): ...
