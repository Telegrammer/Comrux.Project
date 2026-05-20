from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .responsible import (
    Responsible,
    UserResponsible,
    RoleResponsible,
    GroupResponsible,
)


class ProjectTask: ...


class ProjectTaskAssignee(Base):
    __tablename__ = "project_task_assignees"

    task_id: Mapped[UUID] = mapped_column(
        ForeignKey("project_tasks.id_", ondelete="CASCADE"), primary_key=True
    )
    responsible_id: Mapped[int] = mapped_column(
        ForeignKey("responsibles.id_", ondelete="CASCADE"),
        primary_key=True,
    )

    task: Mapped["ProjectTask"] = relationship(back_populates="assignees")
    responsible: Mapped[Responsible] = relationship(lazy="selectin")

