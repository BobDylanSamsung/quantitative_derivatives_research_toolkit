from math import exp, log, sqrt

from scipy.stats import norm

from derivative_pricing.models.market import MarketData
from derivative_pricing.models.options import EuropeanOption


class BlackScholesModel:
    def __init__(
        self,
        option: EuropeanOption,
        market: MarketData,
    ) -> None:
        self.option = option
        self.market = market

    def calculate_call(self) -> float:
        """Calculate the Black-Scholes price of a European call option."""

        return self.market.spot * norm.cdf(self.d1) - self.discounted_strike * norm.cdf(
            self.d2
        )

    def calculate_put(self) -> float:
        """Calculate the Black-Scholes price of a European put option."""

        return self.discounted_strike * norm.cdf(
            -self.d2
        ) - self.market.spot * norm.cdf(-self.d1)

    @property
    def d1(self) -> float:
        """Calculate the Black-Scholes d1 term."""
        numerator = (
            log(self.market.spot / self.option.strike)
            + (self.market.risk_free_rate + 0.5 * self.market.volatility**2)
            * self.option.maturity
        )

        denominator = self.market.volatility * sqrt(self.option.maturity)

        return numerator / denominator

    @property
    def d2(self) -> float:
        """Calculate the Black-Scholes d2 term."""
        return self.d1 - self.market.volatility * sqrt(self.option.maturity)

    @property
    def discounted_strike(self) -> float:
        return self.option.strike * exp(
            -self.market.risk_free_rate * self.option.maturity
        )
