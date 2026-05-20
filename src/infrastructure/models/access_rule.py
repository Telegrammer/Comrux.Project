from uuid import UUID
from sqlalchemy import ForeignKey, Enum, Integer
from sqlalchemy.orm import mapped_column, Mapped, relationship


from domain.enums import ProjectUnitAction

from .base import Base
from .access_rule_responsible import (
    AccessRuleResponsible,
)


class AccessList: ...


class AccessRule(Base):
    responsible_id: Mapped[int] = mapped_column(
        ForeignKey("responsibles.id_", ondelete="CASCADE"), primary_key=True
    )
    action: Mapped[ProjectUnitAction] = mapped_column(
        Enum(ProjectUnitAction), name="action", primary_key=True
    )
    access_list_id: Mapped[UUID] = mapped_column(
        ForeignKey("access_lists.id_", ondelete="CASCADE"), primary_key=True
    )
    is_allow: Mapped[bool] = mapped_column(nullable=False)
    order: Mapped[int] = mapped_column("order", Integer, nullable=False)

    responsible: Mapped[AccessRuleResponsible] = relationship(lazy="selectin")
    access_list: Mapped["AccessList"] = relationship(back_populates="rules")
