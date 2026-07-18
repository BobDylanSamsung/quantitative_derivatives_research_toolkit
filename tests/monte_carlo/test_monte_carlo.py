import math

import numpy as np
import pytest
from numpy.testing import assert_array_equal
from scipy.stats import norm

from derivative_pricing.models.market import MarketData
from derivative_pricing.models.options import EuropeanOption, OptionType
from derivative_pricing.pricing.black_scholes_model import BlackScholesModel
from derivative_pricing.pricing.monte_carlo_model import (
    MonteCarloModel,
    MonteCarloResult,
)


def test_generates_one_draw_per_simulation(
    call_model: MonteCarloModel,
) -> None:
    rng = np.random.default_rng(42)

    draws = call_model.generate_standard_normal_draws(rng)

    assert draws.shape == (call_model.simulations,)
    assert np.issubdtype(draws.dtype, np.floating)


def test_draws_are_reproducible_for_same_seed(
    call_model: MonteCarloModel,
) -> None:
    first_rng = np.random.default_rng(42)
    second_rng = np.random.default_rng(42)

    first_draws = call_model.generate_standard_normal_draws(first_rng)
    second_draws = call_model.generate_standard_normal_draws(second_rng)

    assert_array_equal(first_draws, second_draws)


def test_calculates_terminal_stock_prices(
    call_model: MonteCarloModel,
) -> None:
    draws = np.array([-1.0, 0.0, 1.0])

    actual = call_model.simulate_terminal_stock_prices(draws)

    expected = call_model.market.spot * np.exp(
        call_model.terminal_drift + call_model.terminal_diffusion_scale * draws
    )

    assert actual == pytest.approx(expected)


def test_terminal_stock_prices_are_positive(
    call_model: MonteCarloModel,
) -> None:
    draws = np.array([-10.0, -1.0, 0.0, 1.0, 10.0])

    prices = call_model.simulate_terminal_stock_prices(draws)

    assert np.all(prices > 0.0)


def test_zero_normal_draw_produces_deterministic_component(
    call_model: MonteCarloModel,
) -> None:
    draws = np.array([0.0])

    prices = call_model.simulate_terminal_stock_prices(draws)

    expected = call_model.market.spot * math.exp(call_model.terminal_drift)

    assert prices[0] == pytest.approx(expected)


def test_calculates_call_payoffs(
    market: MarketData,
    call_option: EuropeanOption,
) -> None:
    model = MonteCarloModel(
        option=call_option,
        market=market,
        simulations=3,
    )

    terminal_prices = np.array([90.0, 105.0, 130.0])

    payoffs = model.calculate_terminal_payoffs(terminal_prices)

    expected = np.array([0.0, 0.0, 25.0])

    assert_array_equal(payoffs, expected)


def test_calculates_put_payoffs(
    market: MarketData,
    put_option: EuropeanOption,
) -> None:
    model = MonteCarloModel(
        option=put_option,
        market=market,
        simulations=3,
    )

    terminal_prices = np.array([90.0, 105.0, 130.0])

    payoffs = model.calculate_terminal_payoffs(terminal_prices)

    expected = np.array([15.0, 0.0, 0.0])

    assert_array_equal(payoffs, expected)


def test_payoffs_are_never_negative(
    call_model: MonteCarloModel,
) -> None:
    terminal_prices = np.array([0.0, 50.0, 105.0, 200.0])

    payoffs = call_model.calculate_terminal_payoffs(terminal_prices)

    assert np.all(payoffs >= 0.0)


def test_discounts_terminal_payoffs(
    call_model: MonteCarloModel,
) -> None:
    terminal_payoffs = np.array([0.0, 10.0, 25.0])

    actual = call_model.calculate_discounted_payoffs(terminal_payoffs)

    expected = terminal_payoffs * math.exp(-0.05)

    assert actual == pytest.approx(expected)


def test_calculates_standard_error_using_sample_sd(
    call_model: MonteCarloModel,
) -> None:
    discounted_payoffs = np.array([1.0, 2.0, 3.0, 4.0])

    actual = call_model.standard_error(discounted_payoffs)

    expected = np.std(
        discounted_payoffs,
        ddof=1,
    ) / math.sqrt(discounted_payoffs.size)

    assert actual == pytest.approx(expected)


def test_standard_error_is_zero_for_constant_payoffs(
    call_model: MonteCarloModel,
) -> None:
    discounted_payoffs = np.full(100, 5.0)

    actual = call_model.standard_error(discounted_payoffs)

    assert actual == pytest.approx(0.0)


def test_calculates_95_percent_confidence_interval(
    call_model: MonteCarloModel,
) -> None:
    price = 10.0
    standard_error = 0.50

    lower, upper = call_model.calculate_confidence_interval(
        price=price,
        standard_error=standard_error,
        confidence_level=0.95,
    )

    critical_value = norm.ppf(0.975)
    expected_margin = critical_value * standard_error

    assert lower == pytest.approx(price - expected_margin)
    assert upper == pytest.approx(price + expected_margin)


def test_confidence_interval_is_symmetric(
    call_model: MonteCarloModel,
) -> None:
    price = 10.0

    lower, upper = call_model.calculate_confidence_interval(
        price=price,
        standard_error=0.50,
        confidence_level=0.95,
    )

    assert price - lower == pytest.approx(upper - price)


def test_zero_standard_error_produces_point_interval(
    call_model: MonteCarloModel,
) -> None:
    lower, upper = call_model.calculate_confidence_interval(
        price=10.0,
        standard_error=0.0,
        confidence_level=0.95,
    )

    assert lower == pytest.approx(10.0)
    assert upper == pytest.approx(10.0)


@pytest.mark.parametrize(
    "confidence_level",
    [-1.0, 0.0, 1.0, 1.5],
)
def test_rejects_invalid_confidence_level(
    confidence_level: float,
    call_model: MonteCarloModel,
) -> None:
    with pytest.raises(
        ValueError,
        match="confidence_level must lie between zero and one",
    ):
        call_model.calculate_confidence_interval(
            price=10.0,
            standard_error=0.50,
            confidence_level=confidence_level,
        )


def test_rejects_negative_standard_error(
    call_model: MonteCarloModel,
) -> None:
    with pytest.raises(
        ValueError,
        match="standard_error cannot be negative",
    ):
        call_model.calculate_confidence_interval(
            price=10.0,
            standard_error=-0.50,
            confidence_level=0.95,
        )


def test_simulate_returns_monte_carlo_result(
    call_model: MonteCarloModel,
) -> None:
    result = call_model.simulate()

    assert isinstance(result, MonteCarloResult)
    assert isinstance(result.price, float)
    assert isinstance(result.standard_error, float)
    assert len(result.confidence_interval) == 2


def test_seeded_simulation_is_reproducible(
    call_model: MonteCarloModel,
) -> None:
    first_result = call_model.simulate()
    second_result = call_model.simulate()

    assert first_result == second_result


def test_estimated_price_is_non_negative(
    call_model: MonteCarloModel,
) -> None:
    result = call_model.simulate()

    assert result.price >= 0.0


def test_standard_error_is_non_negative(
    call_model: MonteCarloModel,
) -> None:
    result = call_model.simulate()

    assert result.standard_error >= 0.0


def test_confidence_interval_is_centred_on_price(
    call_model: MonteCarloModel,
) -> None:
    result = call_model.simulate()

    lower, upper = result.confidence_interval

    assert result.price - lower == pytest.approx(upper - result.price)


def test_price_method_returns_simulated_price(
    call_model: MonteCarloModel,
) -> None:
    expected = call_model.simulate().price

    actual = call_model.price()

    assert actual == expected


@pytest.mark.parametrize(
    "option_type",
    [OptionType.CALL, OptionType.PUT],
)
def test_monte_carlo_price_is_consistent_with_black_scholes(
    option_type: OptionType,
) -> None:
    market = MarketData(
        spot=100.0,
        risk_free_rate=0.03,
        volatility=0.20,
    )

    option = EuropeanOption(
        strike=105.0,
        maturity=1.0,
        type=option_type,
    )

    monte_carlo_model = MonteCarloModel(
        option=option,
        market=market,
        simulations=100_000,
        seed=42,
    )

    black_scholes_model = BlackScholesModel(
        option=option,
        market=market,
    )

    result = monte_carlo_model.simulate()
    expected_price = black_scholes_model.price

    assert abs(result.price - expected_price) <= (4.0 * result.standard_error)
