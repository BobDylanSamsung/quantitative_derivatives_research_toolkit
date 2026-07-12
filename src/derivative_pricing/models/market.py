from dataclasses import dataclass


@dataclass(frozen=True)
class MarketData:
    spot: float
    risk_free_rate: float
    volatility: float

