from infrastructure.models import (
    AccessRule,
    AccessRuleGroupResponsible,
    AccessRuleResponsible,
    AccessRuleUserResponsible,
)


def _single_fk_ondelete(column) -> str | None:
    foreign_keys = list(column.foreign_keys)
    assert len(foreign_keys) == 1
    return foreign_keys[0].ondelete


def test_access_rule_responsible_fk_uses_on_delete_cascade() -> None:
    assert _single_fk_ondelete(AccessRule.__table__.c.responsible_id) == "CASCADE"


def test_user_and_group_target_subtype_fk_use_cascade() -> None:
    assert _single_fk_ondelete(AccessRuleUserResponsible.__table__.c.user_id) == "CASCADE"
    assert _single_fk_ondelete(AccessRuleGroupResponsible.__table__.c.group_id) == "CASCADE"
    assert _single_fk_ondelete(AccessRuleUserResponsible.__table__.c.id_) == "CASCADE"
    assert _single_fk_ondelete(AccessRuleGroupResponsible.__table__.c.id_) == "CASCADE"


def test_target_base_table_exists_for_polymorphic_chain() -> None:
    assert AccessRuleResponsible.__table__.name == "responsibles"
