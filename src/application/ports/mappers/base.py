from abc import ABC, abstractmethod


from domain import Entity, Project, User, Directory, Document, ProjectUnit


class DataMapper[TEntity: Entity, Tdto](ABC):

    @abstractmethod
    def to_dto(self, entity: TEntity, old_dto: Tdto | None = None) -> Tdto:
        raise NotImplementedError

    @abstractmethod
    def to_domain(self, dto: Tdto) -> TEntity:
        raise NotImplementedError


class ProjectMapper[Project, Tdto](DataMapper): ...


class UserMapper[User, Tdto](DataMapper): ...


class ProjectUnitMapper[TEntity: ProjectUnit, Tdto](DataMapper): ...


class DirectoryMapper[Tdto](ProjectUnitMapper[Directory, Tdto]): ...


class DocumentMapper[Tdto](ProjectUnitMapper[Document, Tdto]): ...
