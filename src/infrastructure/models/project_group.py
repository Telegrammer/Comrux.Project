from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .project_group_participant import ProjectGroupParticipant


class ProjectGroup(Base):
    id_: Mapped[UUID] = mapped_column(primary_key=True)
    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id_", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    owner_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id_", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(nullable=False)
    color: Mapped[str] = mapped_column(nullable=False)
    is_public: Mapped[bool] = mapped_column(nullable=False, default=False)

    participants: Mapped[list[ProjectGroupParticipant]] = relationship(
        back_populates="group",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (UniqueConstraint("project_id", "name"),)
