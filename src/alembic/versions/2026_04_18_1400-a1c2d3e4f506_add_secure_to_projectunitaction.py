"""add SECURE to projectunitaction enum

Revision ID: a1c2d3e4f506
Revises: 8d2b46f1a9c3
Create Date: 2026-04-18 14:00:00.000000

"""

from typing import Sequence, Union

from alembic import op


revision: str = "a1c2d3e4f506"
down_revision: Union[str, Sequence[str], None] = "8d2b46f1a9c3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE projectunitaction ADD VALUE IF NOT EXISTS 'SECURE'")


def downgrade() -> None:
    # PostgreSQL does not support dropping a single enum label safely.
    pass
