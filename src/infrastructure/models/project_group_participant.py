from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class ProjectGroup: ...


class User: ...


class ProjectGroupParticipant(Base):
    group_id: Mapped[UUID] = mapped_column(
        ForeignKey("project_groups.id_", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id_", ondelete="CASCADE"),
        primary_key=True,
        index=True,
    )

    group: Mapped["ProjectGroup"] = relationship(back_populates="participants")
