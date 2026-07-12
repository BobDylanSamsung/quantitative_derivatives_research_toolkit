from dataclasses import dataclass


@dataclass(frozen=True)
class EuropeanOption:
    strike: float
    maturity: float
