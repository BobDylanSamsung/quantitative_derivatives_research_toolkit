from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class CalibrationMarketData:
    spot: float
    risk_free_rate: float
    dividend_yield: float = 0.0

    def __post_init__(self) -> None:
        if self.spot <= 0:
            raise ValueError("spot must be greater than zero")

    def with_volatility(self, volatility: float) -> "MarketData":
        return MarketData(
            spot=self.spot,
            risk_free_rate=self.risk_free_rate,
            dividend_yield=self.dividend_yield,
            volatility=volatility,
        )


@dataclass(frozen=True, kw_only=True)
class MarketData(CalibrationMarketData):
    volatility: float

    def __post_init__(self) -> None:
        super().__post_init__()

        if self.volatility <= 0:
            raise ValueError("volatility must be greater than zero")
