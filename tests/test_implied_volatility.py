import math

import pytest

from derivative_pricing.models.market import MarketData
from derivative_pricing.models.options import (
    EuropeanOption,
    OptionType,
)
from derivative_pricing.pricing.black_scholes_model import (
    BlackScholesModel,
)
from derivative_pricing.volatility.implied_volatility import (
    ImpliedVolatilitySolver,
)


def calculate_market_price(
    option: EuropeanOption,
    market: MarketData,
) -> float:
    """Calculate a Black-Scholes price for round-trip testing."""
    return BlackScholesModel(
        option=option,
        market=market,
    ).price


@pytest.mark.parametrize(
    "option_type",
    [OptionType.CALL, OptionType.PUT],
)
@pytest.mark.parametrize(
    "expected_volatility",
    [0.10, 0.20, 0.50, 1.00],
)
def test_implied_volatility_round_trip(
    option_type: OptionType,
    expected_volatility: float,
) -> None:
    option = EuropeanOption(
        strike=105.0,
        maturity=0.75,
        type=option_type,
    )

    market = MarketData(
        spot=100.0,
        risk_free_rate=0.04,
        volatility=expected_volatility,
        dividend_yield=0.015,
    )

    market_price = calculate_market_price(
        option=option,
        market=market,
    )

    result = ImpliedVolatilitySolver(
        option=option,
        market=market,
        market_price=market_price,
    ).solve()

    assert result.converged
    assert result.reason is None
    assert result.iterations is not None
    assert result.volatility == pytest.approx(
        expected_volatility,
        abs=1e-8,
    )


@pytest.mark.parametrize(
    ("option_type", "spot", "strike"),
    [
        (OptionType.CALL, 120.0, 100.0),
        (OptionType.PUT, 80.0, 100.0),
    ],
)
def test_price_below_theoretical_lower_bound(
    option_type: OptionType,
    spot: float,
    strike: float,
) -> None:
    option = EuropeanOption(
        strike=strike,
        maturity=1.0,
        type=option_type,
    )

    market = MarketData(
        spot=spot,
        risk_free_rate=0.05,
        volatility=0.20,
        dividend_yield=0.01,
    )

    discounted_spot = spot * math.exp(-market.dividend_yield * option.maturity)
    discounted_strike = strike * math.exp(-market.risk_free_rate * option.maturity)

    match option_type:
        case OptionType.CALL:
            lower_bound = max(
                discounted_spot - discounted_strike,
                0.0,
            )
        case OptionType.PUT:
            lower_bound = max(
                discounted_strike - discounted_spot,
                0.0,
            )
        case _:
            raise AssertionError(f"Unexpected option type: {option_type}")

    result = ImpliedVolatilitySolver(
        option=option,
        market=market,
        market_price=lower_bound - 1e-4,
    ).solve()

    assert not result.converged
    assert result.volatility is None
    assert result.iterations is None
    assert result.reason == "Price below theoretical lower bound"


@pytest.mark.parametrize(
    "option_type",
    [OptionType.CALL, OptionType.PUT],
)
def test_price_above_theoretical_upper_bound(
    option_type: OptionType,
) -> None:
    option = EuropeanOption(
        strike=100.0,
        maturity=1.0,
        type=option_type,
    )

    market = MarketData(
        spot=100.0,
        risk_free_rate=0.05,
        volatility=0.20,
        dividend_yield=0.01,
    )

    discounted_spot = market.spot * math.exp(-market.dividend_yield * option.maturity)
    discounted_strike = option.strike * math.exp(
        -market.risk_free_rate * option.maturity
    )

    match option_type:
        case OptionType.CALL:
            upper_bound = discounted_spot
        case OptionType.PUT:
            upper_bound = discounted_strike
        case _:
            raise AssertionError(f"Unexpected option type: {option_type}")

    result = ImpliedVolatilitySolver(
        option=option,
        market=market,
        market_price=upper_bound + 1e-4,
    ).solve()

    assert not result.converged
    assert result.volatility is None
    assert result.iterations is None
    assert result.reason == "Price above theoretical upper bound"


@pytest.mark.parametrize(
    "maturity",
    [0.0, -0.25],
)
def test_expired_option(
    maturity: float,
) -> None:
    option = EuropeanOption(
        strike=100.0,
        maturity=maturity,
        type=OptionType.CALL,
    )

    market = MarketData(
        spot=100.0,
        risk_free_rate=0.05,
        volatility=0.20,
        dividend_yield=0.01,
    )

    result = ImpliedVolatilitySolver(
        option=option,
        market=market,
        market_price=10.0,
    ).solve()

    assert not result.converged
    assert result.volatility is None
    assert result.iterations is None
    assert result.reason == "Option has expired"


@pytest.mark.parametrize(
    (
        "option_type",
        "spot",
        "strike",
    ),
    [
        # Deep in-the-money call
        (OptionType.CALL, 200.0, 100.0),
        # Deep out-of-the-money call
        (OptionType.CALL, 50.0, 100.0),
        # Deep in-the-money put
        (OptionType.PUT, 50.0, 100.0),
        # Deep out-of-the-money put
        (OptionType.PUT, 200.0, 100.0),
    ],
)
def test_deep_itm_and_otm_options(
    option_type: OptionType,
    spot: float,
    strike: float,
) -> None:
    expected_volatility = 0.40

    option = EuropeanOption(
        strike=strike,
        maturity=2.0,
        type=option_type,
    )

    market = MarketData(
        spot=spot,
        risk_free_rate=0.04,
        volatility=expected_volatility,
        dividend_yield=0.01,
    )

    market_price = calculate_market_price(
        option=option,
        market=market,
    )

    result = ImpliedVolatilitySolver(
        option=option,
        market=market,
        market_price=market_price,
    ).solve()

    assert result.converged
    assert result.reason is None
    assert result.volatility == pytest.approx(
        expected_volatility,
        abs=1e-8,
    )


@pytest.mark.parametrize(
    "option_type",
    [OptionType.CALL, OptionType.PUT],
)
def test_very_short_maturity(
    option_type: OptionType,
) -> None:
    expected_volatility = 0.30

    option = EuropeanOption(
        strike=100.0,
        maturity=1.0 / 365.0,
        type=option_type,
    )

    market = MarketData(
        spot=100.0,
        risk_free_rate=0.04,
        volatility=expected_volatility,
        dividend_yield=0.015,
    )

    market_price = calculate_market_price(
        option=option,
        market=market,
    )

    result = ImpliedVolatilitySolver(
        option=option,
        market=market,
        market_price=market_price,
    ).solve()

    assert result.converged
    assert result.reason is None
    assert result.volatility == pytest.approx(
        expected_volatility,
        abs=1e-8,
    )


@pytest.mark.parametrize(
    "option_type",
    [OptionType.CALL, OptionType.PUT],
)
@pytest.mark.parametrize(
    "expected_volatility",
    [0.10, 0.20, 0.50, 1.00],
)
def test_zero_dividend_regression(
    option_type: OptionType,
    expected_volatility: float,
) -> None:
    """Verify that omitting dividend yield preserves previous behaviour."""

    option = EuropeanOption(
        strike=105.0,
        maturity=0.75,
        type=option_type,
    )

    # dividend_yield uses its default value of zero.
    market = MarketData(
        spot=100.0,
        risk_free_rate=0.04,
        volatility=expected_volatility,
    )

    assert market.dividend_yield == 0.0

    market_price = calculate_market_price(
        option=option,
        market=market,
    )

    result = ImpliedVolatilitySolver(
        option=option,
        market=market,
        market_price=market_price,
    ).solve()

    assert result.converged
    assert result.reason is None
    assert result.volatility == pytest.approx(
        expected_volatility,
        abs=1e-8,
    )
