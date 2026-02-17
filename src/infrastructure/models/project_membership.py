__all__ = ["ProjectMembership"]


from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey, Enum

from domain.enums import ProjectRole
from .base import Base


class Project: ...


class User: ...


class ProjectMembership(Base):

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id_", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id_", ondelete="CASCADE"), primary_key=True, index=True
    )
    role: Mapped[ProjectRole] = mapped_column(
        Enum(ProjectRole, name="projectrole"), nullable=False
    )
    project: Mapped["Project"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship(back_populates="memberships")
