import math
from dataclasses import dataclass, replace

from scipy.optimize import brentq

from derivative_pricing.models.market import MarketData
from derivative_pricing.models.options import EuropeanOption, OptionType
from derivative_pricing.models.volatility import ImpliedVolatilityResult
from derivative_pricing.pricing.black_scholes_model import (
    BlackScholesModel,
)


@dataclass(frozen=True)
class ImpliedVolatilitySolver:
    """Solve for Black-Scholes implied volatility using Brent's method.

    The solver finds the volatility satisfying:

        BlackScholesPrice(volatility) - market_price = 0

    Parameters
    ----------
    option
        European option whose implied volatility is being calculated.
    market
        Market conditions used for pricing. Its volatility value is replaced
        by each candidate volatility evaluated by the solver.
    market_price
        Observed option price.
    minimum_volatility
        Lower endpoint of the Brent root-search bracket.
    maximum_volatility
        Upper endpoint of the Brent root-search bracket.
    price_tolerance
        Tolerance used when checking no-arbitrage price bounds.
    root_tolerance
        Absolute tolerance used by Brent's method.
    maximum_iterations
        Maximum number of Brent iterations.
    """

    option: EuropeanOption
    market: MarketData
    market_price: float

    minimum_volatility: float = 1e-4
    maximum_volatility: float = 5.0

    price_tolerance: float = 1e-8
    root_tolerance: float = 1e-10
    maximum_iterations: int = 100

    def solve(self) -> ImpliedVolatilityResult:
        """Calculate the option's implied volatility."""

        validation_error = self._validate_inputs()

        if validation_error is not None:
            return self._failure(validation_error)

        bounds_error = self._validate_price_bounds()

        if bounds_error is not None:
            return self._failure(bounds_error)

        lower_error = self.pricing_error(self.minimum_volatility)
        upper_error = self.pricing_error(self.maximum_volatility)

        if abs(lower_error) <= self.root_tolerance:
            return self._success(
                volatility=self.minimum_volatility,
                iterations=0,
            )

        if abs(upper_error) <= self.root_tolerance:
            return self._success(
                volatility=self.maximum_volatility,
                iterations=0,
            )

        if lower_error * upper_error > 0:
            return self._failure(
                "No root found inside volatility bracket",
            )

        try:
            volatility, root_result = brentq(
                self.pricing_error,
                self.minimum_volatility,
                self.maximum_volatility,
                xtol=self.root_tolerance,
                maxiter=self.maximum_iterations,
                full_output=True,
                disp=False,
            )
        except (RuntimeError, ValueError) as error:
            return self._failure(str(error))

        if not root_result.converged:
            return ImpliedVolatilityResult(
                volatility=float(volatility),
                converged=False,
                iterations=int(root_result.iterations),
                reason="Brent's method did not converge",
            )

        return self._success(
            volatility=float(volatility),
            iterations=int(root_result.iterations),
        )

    def price_bounds(self) -> tuple[float, float]:
        """Return the no-arbitrage bounds for the option price.

        For a European call:

            max(S * exp(-qT) - K * exp(-rT), 0)
                <= call price <=
            S * exp(-qT)

        For a European put:

            max(K * exp(-rT) - S * exp(-qT), 0)
                <= put price <=
            K * exp(-rT)
        """
        maturity = self.option.maturity

        discounted_spot = self.market.spot * math.exp(
            -self.market.dividend_yield * maturity
        )

        discounted_strike = self.option.strike * math.exp(
            -self.market.risk_free_rate * maturity
        )

        match self.option.type:
            case OptionType.CALL:
                lower_bound = max(
                    discounted_spot - discounted_strike,
                    0.0,
                )
                upper_bound = discounted_spot

            case OptionType.PUT:
                lower_bound = max(
                    discounted_strike - discounted_spot,
                    0.0,
                )
                upper_bound = discounted_strike

            case _:
                raise ValueError(f"Unsupported option type: {self.option.type}")

        return lower_bound, upper_bound

    def pricing_error(self, volatility: float) -> float:
        """Return model price minus observed market price.

        Brent's method searches for a volatility where this function
        equals zero.
        """
        candidate_market = replace(
            self.market,
            volatility=volatility,
        )

        model_price = BlackScholesModel(
            option=self.option,
            market=candidate_market,
        ).price

        return model_price - self.market_price

    def _validate_inputs(self) -> str | None:
        """Return an error message when the solver inputs are invalid."""

        if self.option.strike <= 0:
            return "Strike must be greater than zero"

        if self.option.maturity <= 0:
            return "Option has expired"

        if self.market_price <= 0:
            return "Market price must be positive"

        if self.minimum_volatility <= 0:
            return "Minimum volatility must be greater than zero"

        if self.maximum_volatility <= self.minimum_volatility:
            return "Maximum volatility must be greater than minimum volatility"

        if self.price_tolerance <= 0:
            return "Price tolerance must be greater than zero"

        if self.root_tolerance <= 0:
            return "Root tolerance must be greater than zero"

        if self.maximum_iterations <= 0:
            return "Maximum iterations must be greater than zero"

        return None

    def _validate_price_bounds(self) -> str | None:
        """Check that the observed price satisfies no-arbitrage bounds."""

        lower_bound, upper_bound = self.price_bounds()

        if self.market_price < lower_bound - self.price_tolerance:
            return "Price below theoretical lower bound"

        if self.market_price > upper_bound + self.price_tolerance:
            return "Price above theoretical upper bound"

        return None

    @staticmethod
    def _success(
        volatility: float,
        iterations: int,
    ) -> ImpliedVolatilityResult:
        """Construct a successful solver result."""

        return ImpliedVolatilityResult(
            volatility=volatility,
            converged=True,
            iterations=iterations,
            reason=None,
        )

    @staticmethod
    def _failure(reason: str) -> ImpliedVolatilityResult:
        """Construct an unsuccessful solver result."""

        return ImpliedVolatilityResult(
            volatility=None,
            converged=False,
            iterations=None,
            reason=reason,
        )
