from domain.enums import ProjectRole
from sqlalchemy import UUID, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property

from .base import Base


class User: ...


class ProjectGroup: ...


class AccessRuleTarget(Base):
    id_: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    type_: Mapped[str] = mapped_column(nullable=False)

    __mapper_args__ = {
        "polymorphic_on": type_,
        "polymorphic_identity": "base",
    }


class TargetValueMixin[valT]:
    __abstract__ = True

    @hybrid_property
    def value(self) -> valT:
        raise NotImplementedError


class AccessRuleUserTarget(AccessRuleTarget, TargetValueMixin[UUID]):

    __tablename__ = "access_rule_user_targets"
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id_", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    id_: Mapped[int] = mapped_column(
        ForeignKey("access_rule_targets.id_", ondelete="CASCADE"),
        primary_key=True,
    )

    @hybrid_property
    def value(self) -> UUID:
        return self.user_id

    @value.expression
    def value(cls):
        return cls.user_id

    user: Mapped["User"] = relationship(lazy="joined")

    __mapper_args__ = {
        "polymorphic_identity": "user",
    }


class AccessRuleRoleTarget(AccessRuleTarget, TargetValueMixin[ProjectRole]):

    __tablename__ = "access_rule_role_targets"
    id_: Mapped[int] = mapped_column(
        ForeignKey("access_rule_targets.id_", ondelete="CASCADE"),
        primary_key=True,
    )

    role: Mapped[ProjectRole] = mapped_column(
        Enum(ProjectRole, name="targetrole", create_type=False),
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


class AccessRuleGroupTarget(AccessRuleTarget, TargetValueMixin[UUID]):
    __tablename__ = "access_rule_group_targets"
    id_: Mapped[int] = mapped_column(
        ForeignKey("access_rule_targets.id_", ondelete="CASCADE"),
        primary_key=True,
    )
    group_id: Mapped[UUID] = mapped_column(
        ForeignKey("project_groups.id_", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    @hybrid_property
    def value(self) -> UUID:
        return self.group_id

    @value.expression
    def value(cls):
        return cls.group_id

    group: Mapped["ProjectGroup"] = relationship(lazy="joined")

    __mapper_args__ = {
        "polymorphic_identity": "group",
    }
