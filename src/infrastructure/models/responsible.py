from uuid import UUID

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property

from domain.enums import ProjectRole

from .base import Base


class User: ...


class ProjectGroup: ...


class Responsible(Base):
    id_: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    type_: Mapped[str] = mapped_column(nullable=False)

    __tablename__ = "responsibles"
    __mapper_args__ = {
        "polymorphic_on": type_,
        "polymorphic_identity": "base",
    }


class ResponsibleValueMixin[valT]:
    __abstract__ = True

    @hybrid_property
    def value(self) -> valT:
        raise NotImplementedError


class UserResponsible(Responsible, ResponsibleValueMixin[UUID]):
    __tablename__ = "responsible_users"
    id_: Mapped[int] = mapped_column(
        ForeignKey("responsibles.id_", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id_", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    user: Mapped["User"] = relationship(lazy="joined")

    @hybrid_property
    def value(self) -> UUID:
        return self.user_id

    @value.expression
    def value(cls):
        return cls.user_id

    __mapper_args__ = {
        "polymorphic_identity": "user",
    }


class RoleResponsible(Responsible, ResponsibleValueMixin[ProjectRole]):
    __tablename__ = "responsible_roles"
    id_: Mapped[int] = mapped_column(
        ForeignKey("responsibles.id_", ondelete="CASCADE"),
        primary_key=True,
    )
    role: Mapped[ProjectRole] = mapped_column(
        Enum(ProjectRole, name="project_role", create_type=False),
        unique=True,
        nullable=False,
    )

    @hybrid_property
    def value(self) -> ProjectRole:
        return self.role

    @value.expression
    def value(cls):
        return cls.role

    __mapper_args__ = {
        "polymorphic_identity": "role",
    }


class GroupResponsible(Responsible, ResponsibleValueMixin[UUID]):
    __tablename__ = "responsible_groups"
    id_: Mapped[int] = mapped_column(
        ForeignKey("responsibles.id_", ondelete="CASCADE"),
        primary_key=True,
    )
    group_id: Mapped[UUID] = mapped_column(
        ForeignKey("project_groups.id_", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    group: Mapped["ProjectGroup"] = relationship(lazy="joined")

    @hybrid_property
    def value(self) -> UUID:
        return self.group_id

    @value.expression
    def value(cls):
        return cls.group_id

    __mapper_args__ = {
        "polymorphic_identity": "group",
    }
