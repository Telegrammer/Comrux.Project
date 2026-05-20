"""ensure acl target cascade cleanup

Revision ID: e5f6a7b8193a
Revises: d4e5f6a71829
Create Date: 2026-04-24 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e5f6a7b8193a"
down_revision: Union[str, Sequence[str], None] = "d4e5f6a71829"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _drop_access_rules_target_fk() -> None:
    op.execute(
        """
        DO $$
        DECLARE fk_name text;
        BEGIN
            SELECT c.conname INTO fk_name
            FROM pg_constraint c
            JOIN pg_class t ON t.oid = c.conrelid
            JOIN pg_namespace n ON n.oid = t.relnamespace
            WHERE n.nspname = current_schema()
              AND t.relname = 'access_rules'
              AND c.contype = 'f'
              AND pg_get_constraintdef(c.oid) LIKE 'FOREIGN KEY (target_id)%access_rule_targets%';

            IF fk_name IS NOT NULL THEN
                EXECUTE format('ALTER TABLE access_rules DROP CONSTRAINT %I', fk_name);
            END IF;
        END $$;
        """
    )


def upgrade() -> None:
    op.execute(
        """
        DELETE FROM access_rules ar
        WHERE NOT EXISTS (
            SELECT 1
            FROM access_rule_targets art
            WHERE art.id_ = ar.target_id
        );
        """
    )

    op.execute(
        """
        DELETE FROM access_rule_targets art
        WHERE NOT EXISTS (
                SELECT 1
                FROM access_rule_user_targets urt
                WHERE urt.id_ = art.id_
            )
          AND NOT EXISTS (
                SELECT 1
                FROM access_rule_group_targets grt
                WHERE grt.id_ = art.id_
            )
          AND NOT EXISTS (
                SELECT 1
                FROM access_rule_role_targets rrt
                WHERE rrt.id_ = art.id_
            );
        """
    )

    _drop_access_rules_target_fk()
    op.create_foreign_key(
        "fk_access_rules_target_id_access_rule_targets",
        "access_rules",
        "access_rule_targets",
        ["target_id"],
        ["id_"],
        ondelete="CASCADE",
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION cleanup_access_rule_target_from_subtype()
        RETURNS TRIGGER AS $$
        BEGIN
            DELETE FROM access_rule_targets
            WHERE id_ = OLD.id_;
            RETURN OLD;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.execute(
        "DROP TRIGGER IF EXISTS trg_cleanup_target_on_user_target_delete ON access_rule_user_targets"
    )
    op.execute(
        """
        CREATE TRIGGER trg_cleanup_target_on_user_target_delete
        AFTER DELETE ON access_rule_user_targets
        FOR EACH ROW
        EXECUTE FUNCTION cleanup_access_rule_target_from_subtype()
        """
    )

    op.execute(
        "DROP TRIGGER IF EXISTS trg_cleanup_target_on_group_target_delete ON access_rule_group_targets"
    )
    op.execute(
        """
        CREATE TRIGGER trg_cleanup_target_on_group_target_delete
        AFTER DELETE ON access_rule_group_targets
        FOR EACH ROW
        EXECUTE FUNCTION cleanup_access_rule_target_from_subtype()
        """
    )


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS trg_cleanup_target_on_group_target_delete ON access_rule_group_targets"
    )
    op.execute(
        "DROP TRIGGER IF EXISTS trg_cleanup_target_on_user_target_delete ON access_rule_user_targets"
    )
    op.execute("DROP FUNCTION IF EXISTS cleanup_access_rule_target_from_subtype()")

    _drop_access_rules_target_fk()
    op.create_foreign_key(
        "fk_access_rules_target_id_access_rule_targets",
        "access_rules",
        "access_rule_targets",
        ["target_id"],
        ["id_"],
    )
