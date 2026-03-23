from datetime import date
from uuid import UUID
from sqlalchemy import ForeignKey, Enum
from sqlalchemy.orm import mapped_column, Mapped, relationship, with_polymorphic


from domain.enums import ProjectUnitAction

from .base import Base
from .access_rule_target import (
    AccessRuleTarget,
)


class AccessList: ...


class AccessRule(Base):

    target_id: Mapped[int] = mapped_column(
        ForeignKey("access_rule_targets.id_"), primary_key=True
    )
    action: Mapped[ProjectUnitAction] = mapped_column(
        Enum(ProjectUnitAction), name="action", primary_key=True
    )
    access_list_id: Mapped[UUID] = mapped_column(
        ForeignKey("access_lists.id_", ondelete="CASCADE"), primary_key=True
    )
    is_allow: Mapped[bool] = mapped_column(nullable=False)

    target: Mapped[AccessRuleTarget] = relationship(lazy="selectin")
    access_list: Mapped["AccessList"] = relationship(back_populates="rules")
