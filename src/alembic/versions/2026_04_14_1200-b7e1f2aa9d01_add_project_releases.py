"""add project releases

Revision ID: b7e1f2aa9d01
Revises: 6f1b2b4a9c11
Create Date: 2026-04-14 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b7e1f2aa9d01"
down_revision: Union[str, Sequence[str], None] = "6f1b2b4a9c11"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "project_releases",
        sa.Column("id_", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("requested_by", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "CREATED",
                "PROCESSING",
                "READY",
                "FAILED",
                name="project_release_status",
            ),
            nullable=False,
        ),
        sa.Column("artifact_key", sa.String(), nullable=True),
        sa.Column("file_name", sa.String(), nullable=True),
        sa.Column("archive_size", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id_"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["requested_by"], ["users.id_"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id_"),
    )
    op.create_index(
        "ix_project_releases_project_created",
        "project_releases",
        ["project_id", "created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_project_releases_project_id"),
        "project_releases",
        ["project_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_project_releases_status"),
        "project_releases",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_project_releases_status"), table_name="project_releases")
    op.drop_index(op.f("ix_project_releases_project_id"), table_name="project_releases")
    op.drop_index("ix_project_releases_project_created", table_name="project_releases")
    op.drop_table("project_releases")
    sa.Enum(name="project_release_status").drop(op.get_bind(), checkfirst=True)
