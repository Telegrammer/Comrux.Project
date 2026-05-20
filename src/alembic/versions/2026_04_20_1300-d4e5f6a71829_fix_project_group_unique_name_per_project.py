"""fix project group unique name per project

Revision ID: d4e5f6a71829
Revises: c3d4e5f60718
Create Date: 2026-04-20 13:00:00.000000

"""

from typing import Sequence, Union

from alembic import op


revision: str = "d4e5f6a71829"
down_revision: Union[str, Sequence[str], None] = "c3d4e5f60718"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE project_groups
        DROP CONSTRAINT IF EXISTS project_groups_name_key
        """
    )
    op.execute(
        """
        ALTER TABLE project_groups
        DROP CONSTRAINT IF EXISTS project_groups_project_id_name_key
        """
    )
    op.create_unique_constraint(
        "uq_project_groups_name_project_id",
        "project_groups",
        ["name", "project_id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_project_groups_name_project_id",
        "project_groups",
        type_="unique",
    )
    op.create_unique_constraint(
        "project_groups_project_id_name_key",
        "project_groups",
        ["project_id", "name"],
    )
