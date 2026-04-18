from __future__ import annotations


def unwrap_value(value: object) -> object:
    return getattr(value, "value", value)
