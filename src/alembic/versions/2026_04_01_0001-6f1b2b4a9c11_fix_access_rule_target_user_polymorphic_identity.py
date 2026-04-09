"""fix access rule target user polymorphic identity

Revision ID: 6f1b2b4a9c11
Revises: 7546d0cfa96c
Create Date: 2026-04-01 00:01:00.000000

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "6f1b2b4a9c11"
down_revision: Union[str, Sequence[str], None] = "7546d0cfa96c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        UPDATE access_rule_targets
        SET type_ = 'user'
        WHERE type_ = 'user_id'
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        UPDATE access_rule_targets
        SET type_ = 'user_id'
        WHERE type_ = 'user'
          AND id_ IN (
              SELECT id_
              FROM access_rule_user_targets
          )
        """
    )
