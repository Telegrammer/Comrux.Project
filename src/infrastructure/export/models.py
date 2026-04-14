from datetime import datetime
from uuid import UUID

from sqlalchemy import Enum, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from domain.export import ProjectReleaseStatus
from infrastructure.models.base import Base


class ProjectReleaseOrm(Base):
    __tablename__ = "project_releases"

    id_: Mapped[UUID] = mapped_column(primary_key=True)
    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id_", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    requested_by: Mapped[UUID] = mapped_column(
        ForeignKey("users.id_", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[ProjectReleaseStatus] = mapped_column(
        Enum(ProjectReleaseStatus, name="project_release_status"),
        nullable=False,
        index=True,
    )
    artifact_key: Mapped[str | None] = mapped_column(nullable=True)
    file_name: Mapped[str | None] = mapped_column(nullable=True)
    archive_size: Mapped[int | None] = mapped_column(nullable=True)
    error_message: Mapped[str | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(nullable=True)

    __table_args__ = (
        Index(
            "ix_project_releases_project_created",
            "project_id",
            "created_at",
        ),
    )
