

from dataclasses import dataclass
from ..exceptions import DomainFieldError
from .base import ValueObject

MAX_TITLE_LENGTH = 100


@dataclass
class Title(ValueObject[str]):

    def __post_init__(self):

        if len(self.value) > MAX_TITLE_LENGTH:
            raise DomainFieldError()
                
        for character in self.value:

            if character.isalpha() or character.isdigit() or character in {".", "-", "_"}:
                continue
                
            raise DomainFieldError()
