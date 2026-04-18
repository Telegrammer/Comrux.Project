"""add project groups

Revision ID: 1f3b0a4d9e21
Revises: b7e1f2aa9d01
Create Date: 2026-04-17 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "1f3b0a4d9e21"
down_revision: Union[str, Sequence[str], None] = "b7e1f2aa9d01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "project_groups",
        sa.Column("id_", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("owner_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("color", sa.String(), nullable=False),
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id_"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id_"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id_"),
        sa.UniqueConstraint("project_id", "name"),
    )
    op.create_index(
        op.f("ix_project_groups_project_id"),
        "project_groups",
        ["project_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_project_groups_owner_id"),
        "project_groups",
        ["owner_id"],
        unique=False,
    )

    op.create_table(
        "project_group_participants",
        sa.Column("group_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["group_id"], ["project_groups.id_"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id_"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("group_id", "user_id"),
    )
    op.create_index(
        op.f("ix_project_group_participants_user_id"),
        "project_group_participants",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_project_group_participants_user_id"),
        table_name="project_group_participants",
    )
    op.drop_table("project_group_participants")

    op.drop_index(op.f("ix_project_groups_owner_id"), table_name="project_groups")
    op.drop_index(op.f("ix_project_groups_project_id"), table_name="project_groups")
    op.drop_table("project_groups")
