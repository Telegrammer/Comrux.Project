from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.enums import ProjectTaskStatus
from .base import Base
from .project_task_assignee import ProjectTaskAssignee


class ProjectTask(Base):
    id_: Mapped[UUID] = mapped_column(primary_key=True)
    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id_", ondelete="CASCADE"), nullable=False, index=True
    )
    creator_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id_", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[ProjectTaskStatus] = mapped_column(
        Enum(ProjectTaskStatus, name="project_task_status"), nullable=False, index=True
    )
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    assignees: Mapped[list["ProjectTaskAssignee"]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        Index("ix_project_tasks_project_status_end", "project_id", "status", "end_at"),
    )
