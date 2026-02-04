__all__ = ["User"]


from datetime import date
from uuid import UUID
from sqlalchemy.orm import mapped_column, Mapped, relationship

from .base import Base
from .project_membership import ProjectMembership

class User(Base):
    id_: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    bio: Mapped[str] = mapped_column(nullable=True)
    birthdate: Mapped[date] = mapped_column(nullable=True)
    memberships: Mapped[list[ProjectMembership]] = relationship(
        back_populates="user", cascade="all, delete-orphan", lazy="selectin",
    )
