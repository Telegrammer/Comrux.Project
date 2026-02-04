__all__ = ["BirthDate"]


from datetime import date
from dateutil.relativedelta import relativedelta
from dataclasses import dataclass

from ..exceptions import DomainFieldError
from .base import ValueObject


@dataclass(init=False)
class BirthDate(ValueObject[date]):

    def __init__(
        self, value: date, low_border: date, now: date, age_border: relativedelta
    ):
        self.value = value
        if not (low_border <= self.value <= (now - age_border) or self.value is None):
            raise DomainFieldError("Given value is not a valid birth date")
