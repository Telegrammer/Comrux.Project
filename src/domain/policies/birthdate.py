__all__ = ["BirthDatePolicy"]

from datetime import date
from dateutil.relativedelta import relativedelta
from dataclasses import dataclass


@dataclass
class BirthDatePolicy:

    low_border: date
    age_border: relativedelta
