__all__ = ["FileName"]


from dataclasses import dataclass
from .base import ValueObject
from ..exceptions import DomainFieldError

MAX_NAME_LENGTH = 255


@dataclass
class FileName(ValueObject[str]):

    def __post_init__(self):
        cleaned_value = self._clean_value(self.value)

        if len(cleaned_value) > MAX_NAME_LENGTH:
            raise DomainFieldError(
                f"Name is too long. Maximum {MAX_NAME_LENGTH} characters allowed"
            )

        if not self._is_valid_name(cleaned_value):
            raise DomainFieldError(
                "Name contains invalid characters. Only letters, spaces, dots and hyphens are allowed"
            )

    def _clean_value(self, value: str) -> str:
        if not isinstance(value, str):
            raise DomainFieldError("Name must be a string")

        cleaned = value.strip()

        while "  " in cleaned:
            cleaned = cleaned.replace("  ", " ")

        return cleaned

    def _is_valid_name(self, value: str) -> bool:
        if value == "":
            return True

        if value is None:
            return False

        for character in value:
            if not (
                character.isalpha()
                or character not in {"/", "\\", ":", "*", "?", '"', "<", ">", "|"}
            ):
                return False
        return True
