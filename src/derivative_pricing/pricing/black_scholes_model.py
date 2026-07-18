from math import exp, log, sqrt

from scipy.stats import norm

from derivative_pricing.models.market import MarketData
from derivative_pricing.models.options import EuropeanOption, OptionType


class BlackScholesModel:
    def __init__(
        self,
        option: EuropeanOption,
        market: MarketData,
    ) -> None:
        self.option = option
        self.market = market

    @property
    def price(self) -> float:
        match self.option.type:
            case OptionType.CALL:
                return self.calculate_call()
            case OptionType.PUT:
                return self.calculate_put()
            case _:
                raise ValueError(f"Unsupported option type: {self.option.type}")

    def calculate_call(self) -> float:
        return self.discounted_spot * norm.cdf(
            self.d1
        ) - self.discounted_strike * norm.cdf(self.d2)

    def calculate_put(self) -> float:
        return self.discounted_strike * norm.cdf(
            -self.d2
        ) - self.discounted_spot * norm.cdf(-self.d1)

    @property
    def discounted_spot(self) -> float:
        return self.market.spot * exp(
            -self.market.dividend_yield * self.option.maturity
        )

    @property
    def discounted_strike(self) -> float:
        return self.option.strike * exp(
            -self.market.risk_free_rate * self.option.maturity
        )

    @property
    def d1(self) -> float:
        maturity = self.option.maturity
        volatility = self.market.volatility

        numerator = (
            log(self.market.spot / self.option.strike)
            + (
                self.market.risk_free_rate
                - self.market.dividend_yield
                + 0.5 * volatility**2
            )
            * maturity
        )

        return numerator / (volatility * sqrt(maturity))

    @property
    def d2(self) -> float:
        """Calculate the Black-Scholes d2 term."""
        return self.d1 - self.market.volatility * sqrt(self.option.maturity)
