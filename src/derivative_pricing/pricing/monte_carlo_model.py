import math
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy.stats import norm

from derivative_pricing.models.market import MarketData
from derivative_pricing.models.options import EuropeanOption, OptionType


@dataclass(frozen=True)
class MonteCarloResult:
    """Results produced by a Monte Carlo pricing simulation."""

    price: float
    standard_error: float
    confidence_interval: tuple[float, float]


class MonteCarloModel:
    """Price European options using Monte Carlo simulation.

    The model simulates terminal stock prices under the risk-neutral measure:

        S_T = S_0 * exp(
            (r - 0.5 * sigma**2) * T
            + sigma * sqrt(T) * Z
        )

    where:

        Z ~ N(0, 1)

    The option price is estimated by discounting the average terminal payoff:

        V_0 = exp(-rT) * mean(payoff(S_T))
    """

    def __init__(
        self,
        option: EuropeanOption,
        market: MarketData,
        simulations: int,
        seed: int | None = None,
    ) -> None:
        if simulations < 2:
            raise ValueError("simulations must be at least two")

        self.option = option
        self.market = market
        self.simulations = simulations
        self.seed = seed

    @property
    def discount_factor(self) -> float:
        """Return the discount factor from maturity to the present.

        Formula
        -------
        discount = exp(-rT)
        """
        return math.exp(-self.market.risk_free_rate * self.option.maturity)

    @property
    def terminal_drift(self) -> float:
        """Return the deterministic component of terminal log returns."""
        return (
            self.market.risk_free_rate
            - self.market.dividend_yield
            - 0.5 * self.market.volatility**2
        ) * self.option.maturity

    @property
    def terminal_diffusion_scale(self) -> float:
        """Return the scale applied to each standard-normal draw.

        Formula
        -------
        diffusion_scale = sigma * sqrt(T)
        """
        return self.market.volatility * math.sqrt(self.option.maturity)

    def generate_standard_normal_draws(
        self,
        rng: np.random.Generator,
    ) -> NDArray[np.float64]:
        """Generate independent standard-normal random variables.

        Parameters
        ----------
        rng
            NumPy random-number generator.

        Returns
        -------
        NDArray[np.float64]
            Array containing one draw for each simulation.
        """
        return rng.standard_normal(size=self.simulations)

    def simulate_terminal_stock_prices(
        self,
        standard_normal_draws: NDArray[np.float64],
    ) -> NDArray[np.float64]:
        """Convert standard-normal draws into terminal stock prices.

        Formula
        -------
        S_T = S_0 * exp(drift + diffusion_scale * Z)

        Parameters
        ----------
        standard_normal_draws
            Independent draws from the standard normal distribution.

        Returns
        -------
        NDArray[np.float64]
            Simulated stock prices at maturity.
        """

        terminal_log_returns = (
            self.terminal_drift + self.terminal_diffusion_scale * standard_normal_draws
        )

        return self.market.spot * np.exp(terminal_log_returns)

    def calculate_terminal_payoffs(
        self,
        terminal_stock_prices: NDArray[np.float64],
    ) -> NDArray[np.float64]:
        """Calculate option payoffs at maturity.

        For a call:

            payoff = max(S_T - K, 0)

        For a put:

            payoff = max(K - S_T, 0)
        """
        strike = self.option.strike

        match self.option.type:
            case OptionType.CALL:
                return np.maximum(terminal_stock_prices - strike, 0)

            case OptionType.PUT:
                return np.maximum(strike - terminal_stock_prices, 0)

            case _:
                raise ValueError(f"Unsupported option type: {self.option.type}")

    def calculate_discounted_payoffs(
        self,
        terminal_payoffs: NDArray[np.float64],
    ) -> NDArray[np.float64]:
        """Discount terminal option payoffs to the present."""
        return terminal_payoffs * self.discount_factor

    def standard_error(
        self,
        discounted_payoffs: NDArray[np.float64],
    ) -> float:
        """Estimate the standard error of the simulated option price.

        Formula
        -------
        SE = sample_standard_deviation / sqrt(number_of_simulations)

        Use the sample standard deviation, so NumPy's ``ddof`` should be one.
        """
        sample_sd = np.std(discounted_payoffs, ddof=1)
        return float(sample_sd / math.sqrt(discounted_payoffs.size))

    def calculate_confidence_interval(
        self,
        price: float,
        standard_error: float,
        confidence_level: float,
    ) -> tuple[float, float]:
        """Calculate a normal-approximation confidence interval.

        For a 95% confidence interval:

            price +/- 1.96 * standard_error
        """
        if not 0.0 < confidence_level < 1.0:
            raise ValueError("confidence_level must lie between zero and one")

        if standard_error < 0.0:
            raise ValueError("standard_error cannot be negative")

        alpha = 1.0 - confidence_level
        critical_value = norm.ppf(1.0 - alpha / 2.0)

        margin_of_error = critical_value * standard_error

        return (
            float(price - margin_of_error),
            float(price + margin_of_error),
        )

    def simulate(
        self,
        confidence_level: float = 0.95,
    ) -> MonteCarloResult:
        """Run the Monte Carlo simulation.

        Parameters
        ----------
        confidence_level
            Confidence level used for the normal-approximation
            interval around the Monte Carlo price estimate.

        Returns
        -------
        MonteCarloResult
            Estimated price, standard error, and confidence interval.
        """
        rng = np.random.default_rng(self.seed)

        standard_normal_draws = self.generate_standard_normal_draws(rng)

        terminal_stock_prices = self.simulate_terminal_stock_prices(
            standard_normal_draws
        )

        terminal_payoffs = self.calculate_terminal_payoffs(terminal_stock_prices)

        discounted_payoffs = self.calculate_discounted_payoffs(terminal_payoffs)

        price = float(np.mean(discounted_payoffs))

        standard_error = self.standard_error(discounted_payoffs)

        confidence_interval = self.calculate_confidence_interval(
            price=price,
            standard_error=standard_error,
            confidence_level=confidence_level,
        )

        return MonteCarloResult(
            price=price,
            standard_error=standard_error,
            confidence_interval=confidence_interval,
        )

    def price(self) -> float:
        """Return the Monte Carlo estimate of the option price."""
        return self.simulate().price


if __name__ == "__main__":
    market = MarketData(
        spot=100,
        risk_free_rate=0.05,
        volatility=1,
    )

    option = EuropeanOption(
        strike=120,
        maturity=1,
        type=OptionType.CALL,
    )

    model = MonteCarloModel(
        option=option,
        market=market,
        simulations=100_000,
        seed=42,
    )

    result = model.simulate()

    print(result.price)
    print(result.standard_error)
    print(result.confidence_interval)
