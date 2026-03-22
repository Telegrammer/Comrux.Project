from datetime import date
from uuid import UUID
from sqlalchemy import ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship


from domain.enums import ProjectUnitAction

from .base import Base
from .access_rule import AccessRule


class AccessList(Base):

    id_: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    owner: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id_", ondelete="SET NULL"), nullable=True
    )
    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id_", ondelete="CASCADE"), nullable=False
    )
    rules: Mapped[list[AccessRule]] = relationship(
        back_populates="access_list",
        cascade="all, delete",
        lazy="selectin",
    )

    __table_args__ = (UniqueConstraint(name, project_id),)
