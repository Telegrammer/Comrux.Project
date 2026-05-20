"""unify acl and task responsibles into responsibles catalog

Revision ID: a7b8c9d0315c
Revises: f6a7b8c9204b
Create Date: 2026-04-28 13:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a7b8c9d0315c"
down_revision: Union[str, Sequence[str], None] = "f6a7b8c9204b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _drop_fk(table_name: str, constraint_like: str) -> None:
    op.execute(
        f"""
        DO $$
        DECLARE fk_name text;
        BEGIN
            SELECT c.conname INTO fk_name
            FROM pg_constraint c
            JOIN pg_class t ON t.oid = c.conrelid
            JOIN pg_namespace n ON n.oid = t.relnamespace
            WHERE n.nspname = current_schema()
              AND t.relname = '{table_name}'
              AND c.contype = 'f'
              AND pg_get_constraintdef(c.oid) LIKE '{constraint_like}';

            IF fk_name IS NOT NULL THEN
                EXECUTE format('ALTER TABLE %I DROP CONSTRAINT %I', '{table_name}', fk_name);
            END IF;
        END $$;
        """
    )


def upgrade() -> None:
    op.create_table(
        "responsibles",
        sa.Column("id_", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("type_", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id_"),
    )
    op.create_table(
        "responsible_users",
        sa.Column("id_", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["id_"], ["responsibles.id_"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id_"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id_"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_table(
        "responsible_roles",
        sa.Column("id_", sa.Integer(), nullable=False),
        sa.Column(
            "role",
            sa.Enum("OWNER", "LEAD", "MEMBER", name="project_role", create_type=False),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["id_"], ["responsibles.id_"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id_"),
        sa.UniqueConstraint("role"),
    )
    op.create_table(
        "responsible_groups",
        sa.Column("id_", sa.Integer(), nullable=False),
        sa.Column("group_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["id_"], ["responsibles.id_"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["group_id"], ["project_groups.id_"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id_"),
        sa.UniqueConstraint("group_id"),
    )

    op.execute(
        """
        INSERT INTO responsibles (type_)
        SELECT kind
        FROM (
            SELECT DISTINCT 'user'::text AS kind, urt.user_id::text AS val FROM access_rule_user_targets urt
            UNION
            SELECT DISTINCT 'role'::text AS kind, rrt.role::text AS val FROM access_rule_role_targets rrt
            UNION
            SELECT DISTINCT 'group'::text AS kind, grt.group_id::text AS val FROM access_rule_group_targets grt
            UNION
            SELECT DISTINCT 'user'::text AS kind, urt.user_id::text AS val FROM project_task_user_assignee_targets urt
            UNION
            SELECT DISTINCT 'role'::text AS kind, rrt.role::text AS val FROM project_task_role_assignee_targets rrt
            UNION
            SELECT DISTINCT 'group'::text AS kind, grt.group_id::text AS val FROM project_task_team_assignee_targets grt
        ) all_values
        ORDER BY kind, val
        """
    )
    op.execute(
        """
        INSERT INTO responsible_users (id_, user_id)
        SELECT t.id_, src.user_id::uuid
        FROM (
            SELECT DISTINCT user_id::text AS user_id FROM access_rule_user_targets
            UNION
            SELECT DISTINCT user_id::text AS user_id FROM project_task_user_assignee_targets
        ) src
        JOIN (
            SELECT row_number() OVER (ORDER BY user_id::text) AS rn, user_id
            FROM (
                SELECT DISTINCT user_id FROM (
                    SELECT user_id FROM access_rule_user_targets
                    UNION
                    SELECT user_id FROM project_task_user_assignee_targets
                ) u
            ) all_users
        ) ord ON ord.user_id::text = src.user_id
        JOIN (
            SELECT row_number() OVER (ORDER BY id_) AS rn, id_
            FROM responsibles
            WHERE type_ = 'user'
        ) t ON t.rn = ord.rn
        """
    )
    op.execute(
        """
        INSERT INTO responsible_roles (id_, role)
        SELECT t.id_, src.role::project_role
        FROM (
            SELECT DISTINCT role::text AS role FROM access_rule_role_targets
            UNION
            SELECT DISTINCT role::text AS role FROM project_task_role_assignee_targets
        ) src
        JOIN (
            SELECT row_number() OVER (ORDER BY role) AS rn, role
            FROM (
                SELECT DISTINCT role FROM (
                    SELECT role::text AS role FROM access_rule_role_targets
                    UNION
                    SELECT role::text AS role FROM project_task_role_assignee_targets
                ) r
            ) all_roles
        ) ord ON ord.role = src.role
        JOIN (
            SELECT row_number() OVER (ORDER BY id_) AS rn, id_
            FROM responsibles
            WHERE type_ = 'role'
        ) t ON t.rn = ord.rn
        """
    )
    op.execute(
        """
        INSERT INTO responsible_groups (id_, group_id)
        SELECT t.id_, src.group_id::uuid
        FROM (
            SELECT DISTINCT group_id::text AS group_id FROM access_rule_group_targets
            UNION
            SELECT DISTINCT group_id::text AS group_id FROM project_task_team_assignee_targets
        ) src
        JOIN (
            SELECT row_number() OVER (ORDER BY group_id::text) AS rn, group_id
            FROM (
                SELECT DISTINCT group_id FROM (
                    SELECT group_id FROM access_rule_group_targets
                    UNION
                    SELECT group_id FROM project_task_team_assignee_targets
                ) g
            ) all_groups
        ) ord ON ord.group_id::text = src.group_id
        JOIN (
            SELECT row_number() OVER (ORDER BY id_) AS rn, id_
            FROM responsibles
            WHERE type_ = 'group'
        ) t ON t.rn = ord.rn
        """
    )

    op.execute(
        """
        CREATE TEMP TABLE tmp_acl_responsible_map AS
        SELECT urt.id_ AS old_id, tu.id_ AS new_id
        FROM access_rule_user_targets urt
        JOIN responsible_users tu ON tu.user_id = urt.user_id
        UNION
        SELECT rrt.id_ AS old_id, tr.id_ AS new_id
        FROM access_rule_role_targets rrt
        JOIN responsible_roles tr ON tr.role::text = rrt.role::text
        UNION
        SELECT grt.id_ AS old_id, tg.id_ AS new_id
        FROM access_rule_group_targets grt
        JOIN responsible_groups tg ON tg.group_id = grt.group_id
        """
    )
    op.execute(
        """
        CREATE TEMP TABLE tmp_task_responsible_map AS
        SELECT urt.id_ AS old_id, tu.id_ AS new_id
        FROM project_task_user_assignee_targets urt
        JOIN responsible_users tu ON tu.user_id = urt.user_id
        UNION
        SELECT rrt.id_ AS old_id, tr.id_ AS new_id
        FROM project_task_role_assignee_targets rrt
        JOIN responsible_roles tr ON tr.role::text = rrt.role::text
        UNION
        SELECT grt.id_ AS old_id, tg.id_ AS new_id
        FROM project_task_team_assignee_targets grt
        JOIN responsible_groups tg ON tg.group_id = grt.group_id
        """
    )

    _drop_fk("access_rules", "FOREIGN KEY (target_id)%access_rule_targets%")
    _drop_fk(
        "project_task_assignees", "FOREIGN KEY (target_id)%project_task_assignee_targets%"
    )
    op.alter_column("access_rules", "target_id", new_column_name="responsible_id")
    op.alter_column(
        "project_task_assignees", "target_id", new_column_name="responsible_id"
    )
    op.execute(
        """
        UPDATE access_rules ar
        SET responsible_id = m.new_id
        FROM tmp_acl_responsible_map m
        WHERE ar.responsible_id = m.old_id
        """
    )
    op.execute(
        """
        UPDATE project_task_assignees pta
        SET responsible_id = m.new_id
        FROM tmp_task_responsible_map m
        WHERE pta.responsible_id = m.old_id
        """
    )

    op.create_foreign_key(
        "fk_access_rules_responsible_id_responsibles",
        "access_rules",
        "responsibles",
        ["responsible_id"],
        ["id_"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_project_task_assignees_responsible_id_responsibles",
        "project_task_assignees",
        "responsibles",
        ["responsible_id"],
        ["id_"],
        ondelete="CASCADE",
    )

    op.execute(
        "DROP TRIGGER IF EXISTS trg_cleanup_target_on_group_target_delete ON access_rule_group_targets"
    )
    op.execute(
        "DROP TRIGGER IF EXISTS trg_cleanup_target_on_user_target_delete ON access_rule_user_targets"
    )
    op.execute("DROP FUNCTION IF EXISTS cleanup_access_rule_target_from_subtype()")

    op.drop_table("project_task_team_assignee_targets")
    op.drop_table("project_task_role_assignee_targets")
    op.drop_table("project_task_user_assignee_targets")
    op.drop_table("project_task_assignee_targets")

    op.drop_table("access_rule_group_targets")
    op.drop_table("access_rule_role_targets")
    op.drop_table("access_rule_user_targets")
    op.drop_table("access_rule_targets")


def downgrade() -> None:
    raise NotImplementedError(
        "Downgrade is not supported for responsible catalog unification migration"
    )
