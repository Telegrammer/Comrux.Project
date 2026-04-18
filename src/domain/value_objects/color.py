import re

from dataclasses import dataclass

from .base import ValueObject
from ..exceptions import DomainFieldError

__all__ = ["Color", "HexColor"]


@dataclass(eq=False)
class Color(ValueObject[str]):
    def __eq__(self, other) -> bool:
        return self.value == other.value


@dataclass
class HexColor(Color):
    def __post_init__(self) -> None:
        super().__post_init__()
        pattern = re.compile(r"^#[0-9a-fA-F]{6}$")
        if not pattern.search(self.value):
            raise DomainFieldError("value is not a valid hex color")
