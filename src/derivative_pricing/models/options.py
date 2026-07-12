from dataclasses import dataclass
from enum import StrEnum


class OptionType(StrEnum):
    CALL = "Call"
    PUT = "Put"


@dataclass(frozen=True)
class EuropeanOption:
    strike: float
    maturity: float
    type: OptionType = OptionType.CALL
