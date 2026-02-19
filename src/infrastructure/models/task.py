from uuid import UUID
from datetime import datetime

from sqlalchemy import Enum, Index, text
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.dialects.postgresql import JSONB

from domain.enums import TaskStatus
from .base import Base


class Task(Base):
    id_: Mapped[UUID] = mapped_column(primary_key=True)
    task_type: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, name="status"), nullable=False
    )
    payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False)
    resend_time: Mapped[datetime] = mapped_column(nullable=False)
    attempts: Mapped[int] = mapped_column(nullable=False)


    __table_args__ = (
        Index(
            "ix_tasks_created_resend_time",
            "resend_time",
            postgresql_where=(status == TaskStatus.CREATED),
        ),
    )