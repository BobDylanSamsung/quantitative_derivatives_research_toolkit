import math

import pytest

from derivative_pricing.models.market import MarketData
from derivative_pricing.models.options import EuropeanOption, OptionType
from derivative_pricing.pricing.black_scholes_model import BlackScholesModel
from derivative_pricing.pricing.cox_ross_rubenstein_model import CoxRossRubinsteinModel
from derivative_pricing.pricing.monte_carlo_model import MonteCarloModel

SPOT = 100.0
STRIKE = 100.0
RISK_FREE_RATE = 0.05
DIVIDEND_YIELD = 0.02
VOLATILITY = 0.20
MATURITY = 1.0


@pytest.fixture
def dividend_market() -> MarketData:
    return MarketData(
        spot=SPOT,
        risk_free_rate=RISK_FREE_RATE,
        volatility=VOLATILITY,
        dividend_yield=DIVIDEND_YIELD,
    )


@pytest.fixture
def zero_dividend_market() -> MarketData:
    return MarketData(
        spot=SPOT,
        risk_free_rate=RISK_FREE_RATE,
        volatility=VOLATILITY,
        dividend_yield=0.0,
    )


@pytest.fixture
def call_option() -> EuropeanOption:
    return EuropeanOption(
        strike=STRIKE,
        maturity=MATURITY,
        type=OptionType.CALL,
    )


@pytest.fixture
def put_option() -> EuropeanOption:
    return EuropeanOption(
        strike=STRIKE,
        maturity=MATURITY,
        type=OptionType.PUT,
    )


def test_black_scholes_dividend_adjusted_d1_and_d2(
    dividend_market: MarketData,
    call_option: EuropeanOption,
) -> None:
    model = BlackScholesModel(call_option, dividend_market)

    assert model.d1 == pytest.approx(0.25)
    assert model.d2 == pytest.approx(0.05)


@pytest.mark.parametrize(
    ("option_type", "expected_price"),
    [
        (OptionType.CALL, 9.227005508154036),
        (OptionType.PUT, 6.330080627549918),
    ],
)
def test_black_scholes_known_prices_with_dividend_yield(
    dividend_market: MarketData,
    option_type: OptionType,
    expected_price: float,
) -> None:
    option = EuropeanOption(
        strike=STRIKE,
        maturity=MATURITY,
        type=option_type,
    )

    price = BlackScholesModel(option, dividend_market).price

    assert price == pytest.approx(expected_price, rel=1e-10)


def test_black_scholes_discounted_spot(
    dividend_market: MarketData,
    call_option: EuropeanOption,
) -> None:
    model = BlackScholesModel(call_option, dividend_market)

    expected_discounted_spot = SPOT * math.exp(-DIVIDEND_YIELD * MATURITY)

    assert model.discounted_spot == pytest.approx(expected_discounted_spot)


def test_dividend_adjusted_put_call_parity(
    dividend_market: MarketData,
    call_option: EuropeanOption,
    put_option: EuropeanOption,
) -> None:
    call_price = BlackScholesModel(call_option, dividend_market).price
    put_price = BlackScholesModel(put_option, dividend_market).price

    expected_difference = SPOT * math.exp(
        -DIVIDEND_YIELD * MATURITY
    ) - STRIKE * math.exp(-RISK_FREE_RATE * MATURITY)

    assert call_price - put_price == pytest.approx(expected_difference)


def test_positive_dividend_yield_reduces_call_price(
    dividend_market: MarketData,
    zero_dividend_market: MarketData,
    call_option: EuropeanOption,
) -> None:
    dividend_price = BlackScholesModel(call_option, dividend_market).price
    zero_dividend_price = BlackScholesModel(
        call_option,
        zero_dividend_market,
    ).price

    assert dividend_price < zero_dividend_price


def test_positive_dividend_yield_increases_put_price(
    dividend_market: MarketData,
    zero_dividend_market: MarketData,
    put_option: EuropeanOption,
) -> None:
    dividend_price = BlackScholesModel(put_option, dividend_market).price
    zero_dividend_price = BlackScholesModel(
        put_option,
        zero_dividend_market,
    ).price

    assert dividend_price > zero_dividend_price


def test_crr_uses_dividend_adjusted_risk_neutral_probability(
    dividend_market: MarketData,
    call_option: EuropeanOption,
) -> None:
    model = CoxRossRubinsteinModel(
        option=call_option,
        market=dividend_market,
        steps=100,
    )

    expected_probability = (
        math.exp((RISK_FREE_RATE - DIVIDEND_YIELD) * model.time_step)
        - model.down_factor
    ) / (model.up_factor - model.down_factor)

    assert model.risk_neutral_probability == pytest.approx(expected_probability)


@pytest.mark.parametrize("option_type", [OptionType.CALL, OptionType.PUT])
def test_crr_with_dividends_converges_to_black_scholes(
    dividend_market: MarketData,
    option_type: OptionType,
) -> None:
    option = EuropeanOption(
        strike=STRIKE,
        maturity=MATURITY,
        type=option_type,
    )

    expected_price = BlackScholesModel(option, dividend_market).price

    crr_price = CoxRossRubinsteinModel(
        option=option,
        market=dividend_market,
        steps=1_000,
    ).price()

    assert crr_price == pytest.approx(expected_price, abs=0.005)


def test_monte_carlo_terminal_drift_includes_dividend_yield(
    dividend_market: MarketData,
    call_option: EuropeanOption,
) -> None:
    model = MonteCarloModel(
        option=call_option,
        market=dividend_market,
        simulations=2,
        seed=42,
    )

    expected_drift = (RISK_FREE_RATE - DIVIDEND_YIELD - 0.5 * VOLATILITY**2) * MATURITY

    assert model.terminal_drift == pytest.approx(expected_drift)


@pytest.mark.parametrize("option_type", [OptionType.CALL, OptionType.PUT])
def test_monte_carlo_with_dividends_matches_black_scholes(
    dividend_market: MarketData,
    option_type: OptionType,
) -> None:
    option = EuropeanOption(
        strike=STRIKE,
        maturity=MATURITY,
        type=option_type,
    )

    expected_price = BlackScholesModel(option, dividend_market).price

    result = MonteCarloModel(
        option=option,
        market=dividend_market,
        simulations=200_000,
        seed=42,
    ).simulate(confidence_level=0.99)

    lower_bound, upper_bound = result.confidence_interval

    assert lower_bound <= expected_price <= upper_bound
