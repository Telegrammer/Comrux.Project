"""add order to access rules

Revision ID: c3d4e5f60718
Revises: a1c2d3e4f506
Create Date: 2026-04-20 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c3d4e5f60718"
down_revision: Union[str, Sequence[str], None] = "a1c2d3e4f506"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("access_rules", sa.Column("order", sa.Integer(), nullable=True))

    op.execute(
        """
        WITH ranked_rules AS (
            SELECT
                ar.target_id,
                ar.action,
                ar.access_list_id,
                art.type_ AS target_type,
                ROW_NUMBER() OVER (
                    PARTITION BY ar.access_list_id, art.type_
                    ORDER BY ar.target_id, ar.action
                ) - 1 AS computed_order
            FROM access_rules ar
            JOIN access_rule_targets art ON art.id_ = ar.target_id
        )
        UPDATE access_rules ar
        SET "order" = rr.computed_order
        FROM ranked_rules rr
        WHERE ar.target_id = rr.target_id
          AND ar.action = rr.action
          AND ar.access_list_id = rr.access_list_id
        """
    )

    op.alter_column("access_rules", "order", nullable=False)


def downgrade() -> None:
    op.drop_column("access_rules", "order")
