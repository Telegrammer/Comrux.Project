from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import mapped_column, Mapped, relationship

from .project_membership import ProjectMembership
from .project_unit_node import ProjectUnitNode
from .base import Base


class Project(Base):
    id_: Mapped[UUID] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False)
    updated_at: Mapped[datetime] = mapped_column(nullable=True)
    members: Mapped[list[ProjectMembership]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    units: Mapped[list[ProjectUnitNode]] = relationship(
        back_populates="project",
        cascade="all, delete",
        passive_deletes=True,
        lazy="raise",
    )

    version: Mapped[int] = mapped_column(nullable=False)

    __mapper_args__ = {"version_id_col": version}


@dataclass
class ProjectDto:
    orm_model: Project
    root_directory: UUID | None
