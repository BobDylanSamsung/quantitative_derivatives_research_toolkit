import math

from scipy.stats import norm

from derivative_pricing.models.greeks import Greeks
from derivative_pricing.models.options import OptionType
from derivative_pricing.pricing.black_scholes_model import BlackScholesModel


class BlackScholesGreeks:
    """Calculate analytical Greeks under the Black-Scholes model.

    Assumptions
    -----------
    The formulas assume:

    - The option is European and can only be exercised at expiry.
    - The underlying pays no dividends.
    - The risk-free interest rate is constant and continuously compounded.
    - Volatility is constant over the life of the option.
    - Markets are frictionless, with no transaction costs or taxes.
    - The underlying price follows a geometric Brownian motion.
    - The option maturity is expressed in years.
    """

    def __init__(self, model: BlackScholesModel) -> None:
        self.model = model

    @property
    def greeks(self) -> Greeks:
        return Greeks(
            delta=self.delta,
            gamma=self.gamma,
            vega=self.vega,
            theta=self.theta,
            rho=self.rho,
        )

    @property
    def delta(self) -> float:
        r"""Return the option's Delta.

        Delta measures the sensitivity of the option price to a change in the
        underlying spot price:

        .. math::

            \Delta = \frac{\partial V}{\partial S}

        For a non-dividend-paying European call:

        .. math::

            \Delta_C = N(d_1)

        For a non-dividend-paying European put:

        .. math::

            \Delta_P = N(d_1) - 1

        Intuitively, Delta approximates the change in option value caused by a
        small one-unit change in the underlying price:

        .. math::

            \Delta V \approx \Delta \, \Delta S

        A call Delta lies between 0 and 1, while a put Delta lies between -1
        and 0. Delta is also commonly interpreted as the number of units of the
        underlying required to delta-hedge one option.

        Returns
        -------
        float
            The option price change per one-unit change in spot price.
        """
        match self.model.option.type:
            case OptionType.CALL:
                return float(norm.cdf(self.model.d1))
            case OptionType.PUT:
                return float(norm.cdf(self.model.d1) - 1)
            case _:
                raise ValueError(f"Unsupported option type: {self.model.option.type}")

    @property
    def gamma(self) -> float:
        r"""Return the option's Gamma.

        Gamma measures how quickly Delta changes as the underlying spot price
        changes:

        .. math::

            \Gamma
            =
            \frac{\partial \Delta}{\partial S}
            =
            \frac{\partial^2 V}{\partial S^2}

        Under Black-Scholes:

        .. math::

            \Gamma
            =
            \frac{N'(d_1)}
                 {S \sigma \sqrt{T}}

        where :math:`N'(d_1)` is the standard normal probability density
        function.

        Intuitively, Gamma measures the curvature of the option price with
        respect to spot. A high Gamma means Delta changes rapidly, so a
        delta-hedged position must be rebalanced more frequently.

        Gamma is the same for calls and puts with the same strike, maturity,
        volatility, interest rate and spot price.

        Returns
        -------
        float
            The change in Delta per one-unit change in spot price.
        """
        spot = self.model.market.spot
        volatility = self.model.market.volatility
        maturity = self.model.option.maturity

        return float(
            norm.pdf(self.model.d1) / (spot * volatility * math.sqrt(maturity))
        )

    @property
    def vega(self) -> float:
        r"""Return the option's Vega.

        Vega measures the sensitivity of the option price to a change in
        volatility:

        .. math::

            \text{Vega}
            =
            \frac{\partial V}{\partial \sigma}

        Under Black-Scholes:

        .. math::

            \frac{\partial V}{\partial \sigma}
            =
            S N'(d_1) \sqrt{T}

        Intuitively, higher volatility increases the range of possible future
        underlying prices. Because an option holder benefits from favourable
        price movements while losses are limited to the premium paid, both
        calls and puts generally increase in value as volatility increases.

        This implementation divides the raw derivative by 100:

        .. math::

            \text{Vega}_{1\%}
            =
            \frac{1}{100}
            S N'(d_1) \sqrt{T}

        Therefore, the result represents the approximate option price change
        for a one percentage-point change in volatility, such as a move from
        20% to 21%, rather than a unit change from 0.20 to 1.20.

        Vega is the same for calls and puts with otherwise identical inputs.

        Returns
        -------
        float
            The option price change per one percentage-point change in
            volatility.
        """
        spot = self.model.market.spot
        maturity = self.model.option.maturity

        return float(spot * norm.pdf(self.model.d1) * math.sqrt(maturity) / 100)

    @property
    def theta(self) -> float:
        r"""Return the option's Theta.

        Theta measures the change in option value as calendar time passes.
        When :math:`T` denotes time remaining until expiry, the conventional
        trading definition is:

        .. math::

            \Theta = -\frac{\partial V}{\partial T}

        This sign convention reflects that one day passing reduces the
        remaining time to expiry.

        For a non-dividend-paying European call:

        .. math::

            \Theta_C
            =
            -\frac{S N'(d_1)\sigma}{2\sqrt{T}}
            -
            rKe^{-rT}N(d_2)

        For a non-dividend-paying European put:

        .. math::

            \Theta_P
            =
            -\frac{S N'(d_1)\sigma}{2\sqrt{T}}
            +
            rKe^{-rT}N(-d_2)

        Intuitively, Theta measures time decay. As expiry approaches, an
        option has less time for the underlying to move favourably, so its
        time value generally declines. Theta is therefore commonly negative
        for long option positions, although some put configurations can have
        positive Theta.

        The analytical formulas produce annual Theta because maturity is
        measured in years. This implementation divides by 365 so the result
        represents the approximate price change for one calendar day passing.

        Returns
        -------
        float
            The option price change per calendar day.
        """
        spot = self.model.market.spot
        strike = self.model.option.strike
        maturity = self.model.option.maturity
        volatility = self.model.market.volatility
        risk_free_rate = self.model.market.risk_free_rate

        diffusion_term = (
            -spot * norm.pdf(self.model.d1) * volatility / (2 * math.sqrt(maturity))
        )

        discounted_strike = strike * math.exp(-risk_free_rate * maturity)

        match self.model.option.type:
            case OptionType.CALL:
                theta_per_year = diffusion_term - (
                    risk_free_rate * discounted_strike * norm.cdf(self.model.d2)
                )
            case OptionType.PUT:
                theta_per_year = diffusion_term + (
                    risk_free_rate * discounted_strike * norm.cdf(-self.model.d2)
                )
            case _:
                raise ValueError(f"Unsupported option type: {self.model.option.type}")

        return float(theta_per_year / 365)

    @property
    def rho(self) -> float:
        r"""Return the option's Rho.

        Rho measures the sensitivity of the option price to a change in the
        continuously compounded risk-free interest rate:

        .. math::

            \rho = \frac{\partial V}{\partial r}

        For a non-dividend-paying European call:

        .. math::

            \rho_C
            =
            KTe^{-rT}N(d_2)

        For a non-dividend-paying European put:

        .. math::

            \rho_P
            =
            -KTe^{-rT}N(-d_2)

        Intuitively, a higher interest rate reduces the present value of the
        strike price. This generally increases call values and decreases put
        values, which is why call Rho is positive and put Rho is negative.

        This implementation divides the raw derivative by 100:

        .. math::

            \rho_{1\%}
            =
            \frac{1}{100}
            \frac{\partial V}{\partial r}

        Therefore, the result represents the approximate option price change
        for a one percentage-point interest-rate change, such as a move from
        5% to 6%, rather than a unit change from 0.05 to 1.05.

        Returns
        -------
        float
            The option price change per one percentage-point change in the
            risk-free rate.
        """
        strike = self.model.option.strike
        maturity = self.model.option.maturity
        risk_free_rate = self.model.market.risk_free_rate

        discounted_strike = strike * math.exp(-risk_free_rate * maturity)

        match self.model.option.type:
            case OptionType.CALL:
                rho = maturity * discounted_strike * norm.cdf(self.model.d2)
            case OptionType.PUT:
                rho = -maturity * discounted_strike * norm.cdf(-self.model.d2)
            case _:
                raise ValueError(f"Unsupported option type: {self.model.option.type}")

        return float(rho / 100)
