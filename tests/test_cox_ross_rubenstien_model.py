import math

import pytest

from derivative_pricing.models.market import MarketData
from derivative_pricing.models.options import EuropeanOption, OptionType
from derivative_pricing.pricing.black_scholes_model import BlackScholesModel
from derivative_pricing.pricing.cox_ross_rubenstein_model import CoxRossRubinsteinModel

SPOT = 100.0
STRIKE = 100.0
MATURITY = 1.0
RISK_FREE_RATE = 0.05
VOLATILITY = 0.20


def build_model(
    option_type: OptionType,
    *,
    steps: int = 1,
    spot: float = SPOT,
    strike: float = STRIKE,
    maturity: float = MATURITY,
    risk_free_rate: float = RISK_FREE_RATE,
    volatility: float = VOLATILITY,
) -> CoxRossRubinsteinModel:
    option = EuropeanOption(
        strike=strike,
        maturity=maturity,
        type=option_type,
    )

    market = MarketData(
        spot=spot,
        risk_free_rate=risk_free_rate,
        volatility=volatility,
    )

    return CoxRossRubinsteinModel(
        option=option,
        market=market,
        steps=steps,
    )


@pytest.mark.parametrize("steps", [0, -1, -100])
def test_rejects_non_positive_step_count(steps: int) -> None:
    with pytest.raises(
        ValueError,
        match="steps must be greater than zero",
    ):
        build_model(
            OptionType.CALL,
            steps=steps,
        )


def test_time_step() -> None:
    model = build_model(
        OptionType.CALL,
        steps=4,
        maturity=1.0,
    )

    assert model.time_step == pytest.approx(0.25)


def test_up_factor() -> None:
    model = build_model(
        OptionType.CALL,
        steps=4,
        maturity=1.0,
        volatility=0.20,
    )

    expected = math.exp(0.20 * math.sqrt(0.25))

    assert model.up_factor == pytest.approx(expected)


def test_down_factor_is_inverse_of_up_factor() -> None:
    model = build_model(
        OptionType.CALL,
        steps=4,
    )

    assert model.down_factor == pytest.approx(1 / model.up_factor)
    assert model.up_factor * model.down_factor == pytest.approx(1.0)


def test_discount_factor() -> None:
    model = build_model(
        OptionType.CALL,
        steps=4,
        maturity=1.0,
        risk_free_rate=0.05,
    )

    expected = math.exp(-0.05 * 0.25)

    assert model.discount_factor == pytest.approx(expected)


def test_risk_neutral_probability() -> None:
    model = build_model(
        OptionType.CALL,
        steps=1,
    )

    expected = (
        math.exp(RISK_FREE_RATE * MATURITY)
        - math.exp(-VOLATILITY * math.sqrt(MATURITY))
    ) / (
        math.exp(VOLATILITY * math.sqrt(MATURITY))
        - math.exp(-VOLATILITY * math.sqrt(MATURITY))
    )

    assert model.risk_neutral_probability == pytest.approx(expected)
    assert model.risk_neutral_probability == pytest.approx(0.5774931963561243)


def test_terminal_stock_prices_for_one_step() -> None:
    model = build_model(
        OptionType.CALL,
        steps=1,
    )

    expected = [
        SPOT * model.down_factor,
        SPOT * model.up_factor,
    ]

    assert model.terminal_stock_prices() == pytest.approx(expected)


def test_terminal_stock_prices_for_two_steps() -> None:
    model = build_model(
        OptionType.CALL,
        steps=2,
    )

    expected = [
        SPOT * model.down_factor**2,
        SPOT * model.up_factor * model.down_factor,
        SPOT * model.up_factor**2,
    ]

    assert model.terminal_stock_prices() == pytest.approx(expected)

    # In CRR, one up and one down recombine to the initial spot price.
    assert model.terminal_stock_prices()[1] == pytest.approx(SPOT)


def test_terminal_stock_price_count() -> None:
    steps = 20
    model = build_model(
        OptionType.CALL,
        steps=steps,
    )

    assert len(model.terminal_stock_prices()) == steps + 1


def test_terminal_stock_prices_are_ascending() -> None:
    model = build_model(
        OptionType.CALL,
        steps=10,
    )

    prices = model.terminal_stock_prices()

    assert prices == sorted(prices)


def test_call_terminal_payoffs() -> None:
    model = build_model(
        OptionType.CALL,
        steps=1,
    )

    stock_prices = model.terminal_stock_prices()
    expected = [max(stock_price - STRIKE, 0.0) for stock_price in stock_prices]

    assert model.terminal_payoffs() == pytest.approx(expected)
    assert model.terminal_payoffs() == pytest.approx([0.0, 22.14027581601698])


def test_put_terminal_payoffs() -> None:
    model = build_model(
        OptionType.PUT,
        steps=1,
    )

    stock_prices = model.terminal_stock_prices()
    expected = [max(STRIKE - stock_price, 0.0) for stock_price in stock_prices]

    assert model.terminal_payoffs() == pytest.approx(expected)
    assert model.terminal_payoffs() == pytest.approx([18.12692469220181, 0.0])


def test_one_step_call_price() -> None:
    model = build_model(
        OptionType.CALL,
        steps=1,
    )

    assert model.price() == pytest.approx(
        12.162284964623943,
        abs=1e-12,
    )


def test_one_step_put_price() -> None:
    model = build_model(
        OptionType.PUT,
        steps=1,
    )

    assert model.price() == pytest.approx(
        7.285227414695337,
        abs=1e-12,
    )


@pytest.mark.parametrize(
    "option_type",
    [
        OptionType.CALL,
        OptionType.PUT,
    ],
)
def test_price_converges_towards_black_scholes(
    option_type: OptionType,
) -> None:
    option = EuropeanOption(
        strike=STRIKE,
        maturity=MATURITY,
        type=option_type,
    )
    market = MarketData(
        spot=SPOT,
        risk_free_rate=RISK_FREE_RATE,
        volatility=VOLATILITY,
    )

    crr_model = CoxRossRubinsteinModel(
        option=option,
        market=market,
        steps=3_000,
    )
    black_scholes_model = BlackScholesModel(
        option=option,
        market=market,
    )

    match option_type:
        case OptionType.CALL:
            expected_price = black_scholes_model.calculate_call()
        case OptionType.PUT:
            expected_price = black_scholes_model.calculate_put()
        case _:
            raise ValueError(f"Unsupported option type: {option_type}")

    assert crr_model.price() == pytest.approx(
        expected_price,
        abs=0.01,
    )


@pytest.mark.parametrize("steps", [1, 2, 10, 100, 500])
def test_put_call_parity(steps: int) -> None:
    call_model = build_model(
        OptionType.CALL,
        steps=steps,
    )
    put_model = build_model(
        OptionType.PUT,
        steps=steps,
    )

    discounted_strike = STRIKE * math.exp(-RISK_FREE_RATE * MATURITY)

    assert call_model.price() - put_model.price() == pytest.approx(
        SPOT - discounted_strike,
        abs=1e-10,
    )


def test_deep_in_the_money_call_has_positive_value() -> None:
    model = build_model(
        OptionType.CALL,
        steps=100,
        spot=200.0,
        strike=100.0,
    )

    assert model.price() > 0
    assert model.price() >= 200.0 - 100.0


def test_deep_in_the_money_put_has_positive_value() -> None:
    model = build_model(
        OptionType.PUT,
        steps=100,
        spot=50.0,
        strike=100.0,
    )

    assert model.price() > 0
