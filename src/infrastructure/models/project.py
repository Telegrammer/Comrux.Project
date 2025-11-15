__all__ = ["Project"]


from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import mapped_column, Mapped, relationship

from .base import Base


class Project(Base):
    id_: Mapped[UUID] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False)
