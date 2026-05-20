"""add project tasks

Revision ID: f6a7b8c9204b
Revises: e5f6a7b8193a
Create Date: 2026-04-25 13:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f6a7b8c9204b"
down_revision: Union[str, Sequence[str], None] = "e5f6a7b8193a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # project_task_status = sa.Enum(
    #     "PLANNED",
    #     "IN_PROGRESS",
    #     "DONE",
    #     "OVERDUE",
    #     "CANCELED",
    #     name="project_task_status",
    # )
    # project_task_status.create(bind, checkfirst=True)

    op.create_table(
        "project_tasks",
        sa.Column("id_", sa.UUID(), nullable=False),
        sa.Column("project_id", sa.UUID(), nullable=False),
        sa.Column("creator_id", sa.UUID(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column(
            "status",
            sa.Enum(
                "PLANNED",
                "IN_PROGRESS",
                "DONE",
                "OVERDUE",
                "CANCELED",
                name="project_task_status",
            ),
            nullable=False,
        ),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["creator_id"], ["users.id_"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id_"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id_"),
    )
    op.create_index(
        "ix_project_tasks_project_status_end",
        "project_tasks",
        ["project_id", "status", "end_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_project_tasks_project_id"),
        "project_tasks",
        ["project_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_project_tasks_creator_id"),
        "project_tasks",
        ["creator_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_project_tasks_status"),
        "project_tasks",
        ["status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_project_tasks_created_at"),
        "project_tasks",
        ["created_at"],
        unique=False,
    )

    op.create_table(
        "project_task_assignee_targets",
        sa.Column("id_", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("type_", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id_"),
    )
    op.create_table(
        "project_task_user_assignee_targets",
        sa.Column("id_", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["id_"], ["project_task_assignee_targets.id_"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id_"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id_"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_table(
        "project_task_role_assignee_targets",
        sa.Column("id_", sa.Integer(), nullable=False),
        sa.Column(
            "role",
            sa.Enum("OWNER", "LEAD", "MEMBER", name="project_role"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["id_"], ["project_task_assignee_targets.id_"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id_"),
        sa.UniqueConstraint("role"),
    )
    op.create_table(
        "project_task_team_assignee_targets",
        sa.Column("id_", sa.Integer(), nullable=False),
        sa.Column("group_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["id_"], ["project_task_assignee_targets.id_"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["group_id"], ["project_groups.id_"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id_"),
        sa.UniqueConstraint("group_id"),
    )
    op.create_table(
        "project_task_assignees",
        sa.Column("task_id", sa.UUID(), nullable=False),
        sa.Column("target_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["task_id"], ["project_tasks.id_"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["target_id"], ["project_task_assignee_targets.id_"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("task_id", "target_id"),
    )
    op.create_index(
        op.f("ix_project_task_assignees_task_id"),
        "project_task_assignees",
        ["task_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_project_task_assignees_task_id"), table_name="project_task_assignees"
    )
    op.drop_table("project_task_assignees")
    op.drop_table("project_task_team_assignee_targets")
    op.drop_table("project_task_role_assignee_targets")
    op.drop_table("project_task_user_assignee_targets")
    op.drop_table("project_task_assignee_targets")

    op.drop_index(op.f("ix_project_tasks_created_at"), table_name="project_tasks")
    op.drop_index(op.f("ix_project_tasks_status"), table_name="project_tasks")
    op.drop_index(op.f("ix_project_tasks_creator_id"), table_name="project_tasks")
    op.drop_index(op.f("ix_project_tasks_project_id"), table_name="project_tasks")
    op.drop_index("ix_project_tasks_project_status_end", table_name="project_tasks")
    op.drop_table("project_tasks")

    bind = op.get_bind()
    sa.Enum(name="project_task_status").drop(bind, checkfirst=True)
