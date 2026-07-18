from dataclasses import dataclass


@dataclass(frozen=True)
class MarketData:
    spot: float
    risk_free_rate: float
    volatility: float
    dividend_yield: float = 0.0

    def __post_init__(self) -> None:
        if self.spot <= 0:
            raise ValueError("spot must be greater than zero")

        if self.volatility <= 0:
            raise ValueError("volatility must be greater than zero")
