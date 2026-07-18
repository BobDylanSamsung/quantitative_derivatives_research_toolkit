import math

from derivative_pricing.models.market import MarketData
from derivative_pricing.models.options import EuropeanOption, OptionType


class CoxRossRubinsteinModel:
    """Price European options using a Cox-Ross-Rubinstein binomial tree."""

    def __init__(
        self,
        option: EuropeanOption,
        market: MarketData,
        steps: int,
    ) -> None:
        if steps <= 0:
            raise ValueError("steps must be greater than zero")

        self.option = option
        self.market = market
        self.steps = steps

    @property
    def time_step(self) -> float:
        """Return the length of each tree step in years.

        Formula
        -------
        dt = T / N
        """
        return self.option.maturity / self.steps

    @property
    def up_factor(self) -> float:
        """Return the multiplicative stock-price factor for an up move.

        Formula
        -------
        u = exp(sigma * sqrt(dt))
        """
        return math.exp(self.market.volatility * math.sqrt(self.time_step))

    @property
    def down_factor(self) -> float:
        return 1 / self.up_factor

    @property
    def risk_neutral_probability(self) -> float:
        """Return the risk-neutral probability of an up move.


        The resulting probability must lie between zero and one for the tree
        to be arbitrage-free.
        """
        return (
            math.exp(
                (self.market.risk_free_rate - self.market.dividend_yield)
                * self.time_step
            )
            - self.down_factor
        ) / (self.up_factor - self.down_factor)

    @property
    def discount_factor(self) -> float:
        """Return the one-step risk-free discount factor.

        Formula
        -------
        discount = exp(-r * dt)
        """
        return math.exp(-self.market.risk_free_rate * self.time_step)

    def terminal_stock_prices(self) -> list[float]:
        """Return stock prices at the option's maturity.

        For terminal node j, where j is the number of up moves:

        S_j = S_0 * u^j * d^(N-j)

        Returns
        -------
        list[float]
            The N + 1 possible terminal stock prices.
        """

        def _calculate_price_after_j_ups(j: int) -> float:
            return (
                self.market.spot
                * self.up_factor**j
                * self.down_factor ** (self.steps - j)
            )

        return [_calculate_price_after_j_ups(j) for j in range(0, self.steps + 1)]

    def terminal_payoffs(self) -> list[float]:
        stock_prices = self.terminal_stock_prices()
        strike = self.option.strike

        match self.option.type:
            case OptionType.CALL:
                return [max(stock_price - strike, 0.0) for stock_price in stock_prices]

            case OptionType.PUT:
                return [max(strike - stock_price, 0.0) for stock_price in stock_prices]

            case _:
                raise ValueError(f"Unsupported option type: {self.option.type}")

    def price(self) -> float:
        """Return the option price using backward induction.

        Starting from the terminal payoffs, each earlier node is calculated as:

        V = exp(-r * dt) * (p * V_up + (1 - p) * V_down)

        Returns
        -------
        float
            The value at the root of the binomial tree.
        """
        probability_up = self.risk_neutral_probability
        probability_down = 1 - probability_up
        discount = self.discount_factor

        def _calculate_parent_row(values: list[float]) -> list[float]:
            return [
                discount
                * (
                    probability_up * values[index + 1]
                    + probability_down * values[index]
                )
                for index in range(len(values) - 1)
            ]

        current_values = self.terminal_payoffs()

        while len(current_values) > 1:
            current_values = _calculate_parent_row(current_values)

        return current_values[0]
