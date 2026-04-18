"""add access rule group targets

Revision ID: 8d2b46f1a9c3
Revises: 1f3b0a4d9e21
Create Date: 2026-04-18 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8d2b46f1a9c3"
down_revision: Union[str, Sequence[str], None] = "1f3b0a4d9e21"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "access_rule_group_targets",
        sa.Column("id_", sa.Integer(), nullable=False),
        sa.Column("group_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["group_id"], ["project_groups.id_"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["id_"], ["access_rule_targets.id_"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id_"),
        sa.UniqueConstraint("group_id"),
    )


def downgrade() -> None:
    op.drop_table("access_rule_group_targets")
