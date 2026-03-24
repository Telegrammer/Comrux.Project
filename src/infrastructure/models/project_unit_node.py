from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey, UniqueConstraint, Index, Enum
from sqlalchemy.dialects.postgresql import JSONB

from domain.enums import ProjectUnitType


from .base import Base


class Project: ...


class ProjectUnitNode(Base):
    id_: Mapped[UUID] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False)
    attributes: Mapped[dict] = mapped_column(JSONB, nullable=False)
    unit_type: Mapped[ProjectUnitType] = mapped_column(
        Enum(ProjectUnitType, name="unit_type"), nullable=False, index=True
    )

    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id_", ondelete="CASCADE"), nullable=False, index=True
    )
    created_by: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id_", ondelete="SET NULL"), nullable=True
    )
    parent_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("project_unit_nodes.id_", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    access_list_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("access_lists.id_", ondelete="SET NULL")
    )

    parent: Mapped[Optional["ProjectUnitNode"]] = relationship(remote_side=[id_])
    project: Mapped["Project"] = relationship(back_populates="units")

    __table_args__ = (
        UniqueConstraint(name, parent_id, project_id),
        Index(
            "ix_project_single_root",
            "project_id",
            unique=True,
            postgresql_where=(parent_id.is_(None)),
        ),
    )

    __mapper_args__ = {"polymorphic_on": unit_type, "polymorphic_identity": "unit"}


class DirectoryNode(ProjectUnitNode):
    __tablename__ = None
    __mapper_args__ = {"polymorphic_identity": ProjectUnitType.DIRECTORY.value}


class DocumentNode(ProjectUnitNode):
    __tablename__ = None
    __mapper_args__ = {"polymorphic_identity": ProjectUnitType.DOCUMENT.value}
