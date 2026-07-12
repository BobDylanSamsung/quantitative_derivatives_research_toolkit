import pytest

from derivative_pricing.greeks.greeks import BlackScholesGreeks
from derivative_pricing.models.market import MarketData
from derivative_pricing.models.options import EuropeanOption, OptionType
from derivative_pricing.pricing.black_scholes_model import BlackScholesModel

SPOT = 100.0
STRIKE = 100.0
MATURITY = 1.0
RISK_FREE_RATE = 0.05
VOLATILITY = 0.20


def build_model(
    option_type: OptionType,
    *,
    spot: float = SPOT,
    strike: float = STRIKE,
    maturity: float = MATURITY,
    risk_free_rate: float = RISK_FREE_RATE,
    volatility: float = VOLATILITY,
) -> BlackScholesModel:
    market = MarketData(
        spot=spot,
        risk_free_rate=risk_free_rate,
        volatility=volatility,
    )

    option = EuropeanOption(
        strike=strike,
        maturity=maturity,
        type=option_type,
    )

    return BlackScholesModel(
        option=option,
        market=market,
    )


def calculate_price(model: BlackScholesModel) -> float:
    match model.option.type:
        case OptionType.CALL:
            return model.calculate_call()
        case OptionType.PUT:
            return model.calculate_put()
        case _:
            raise ValueError(f"Unsupported option type: {model.option.type}")


@pytest.fixture
def call_model() -> BlackScholesModel:
    return build_model(OptionType.CALL)


@pytest.fixture
def put_model() -> BlackScholesModel:
    return build_model(OptionType.PUT)


@pytest.fixture
def call_greeks(call_model: BlackScholesModel) -> BlackScholesGreeks:
    return BlackScholesGreeks(call_model)


@pytest.fixture
def put_greeks(put_model: BlackScholesModel) -> BlackScholesGreeks:
    return BlackScholesGreeks(put_model)


@pytest.mark.parametrize(
    ("option_type", "expected_delta"),
    [
        (OptionType.CALL, 0.63683065),
        (OptionType.PUT, -0.36316935),
    ],
)
def test_delta(option_type: OptionType, expected_delta: float) -> None:
    greeks = BlackScholesGreeks(build_model(option_type))

    assert greeks.delta == pytest.approx(expected_delta, abs=1e-8)


@pytest.mark.parametrize(
    "option_type",
    [
        OptionType.CALL,
        OptionType.PUT,
    ],
)
def test_gamma(option_type: OptionType) -> None:
    greeks = BlackScholesGreeks(build_model(option_type))

    assert greeks.gamma == pytest.approx(0.01876202, abs=1e-8)


@pytest.mark.parametrize(
    "option_type",
    [
        OptionType.CALL,
        OptionType.PUT,
    ],
)
def test_vega(option_type: OptionType) -> None:
    greeks = BlackScholesGreeks(build_model(option_type))

    # Vega is expressed per one percentage-point change in volatility.
    assert greeks.vega == pytest.approx(0.37524035, abs=1e-8)


@pytest.mark.parametrize(
    ("option_type", "expected_theta"),
    [
        (OptionType.CALL, -0.01757268),
        (OptionType.PUT, -0.00454214),
    ],
)
def test_theta(option_type: OptionType, expected_theta: float) -> None:
    greeks = BlackScholesGreeks(build_model(option_type))

    # Theta is expressed per calendar day.
    assert greeks.theta == pytest.approx(expected_theta, abs=1e-8)


@pytest.mark.parametrize(
    ("option_type", "expected_rho"),
    [
        (OptionType.CALL, 0.53232482),
        (OptionType.PUT, -0.41890461),
    ],
)
def test_rho(option_type: OptionType, expected_rho: float) -> None:
    greeks = BlackScholesGreeks(build_model(option_type))

    # Rho is expressed per one percentage-point change in the risk-free rate.
    assert greeks.rho == pytest.approx(expected_rho, abs=1e-8)


def test_call_put_delta_parity(
    call_greeks: BlackScholesGreeks,
    put_greeks: BlackScholesGreeks,
) -> None:
    assert call_greeks.delta - put_greeks.delta == pytest.approx(
        1.0,
        abs=1e-12,
    )


def test_call_and_put_gamma_are_equal(
    call_greeks: BlackScholesGreeks,
    put_greeks: BlackScholesGreeks,
) -> None:
    assert call_greeks.gamma == pytest.approx(
        put_greeks.gamma,
        abs=1e-12,
    )


def test_call_and_put_vega_are_equal(
    call_greeks: BlackScholesGreeks,
    put_greeks: BlackScholesGreeks,
) -> None:
    assert call_greeks.vega == pytest.approx(
        put_greeks.vega,
        abs=1e-12,
    )


@pytest.mark.parametrize(
    "option_type",
    [
        OptionType.CALL,
        OptionType.PUT,
    ],
)
def test_delta_matches_finite_difference(option_type: OptionType) -> None:
    step = 1e-3

    price_above = calculate_price(
        build_model(
            option_type,
            spot=SPOT + step,
        )
    )
    price_below = calculate_price(
        build_model(
            option_type,
            spot=SPOT - step,
        )
    )

    numerical_delta = (price_above - price_below) / (2 * step)
    analytical_delta = BlackScholesGreeks(build_model(option_type)).delta

    assert analytical_delta == pytest.approx(
        numerical_delta,
        rel=1e-6,
        abs=1e-8,
    )


@pytest.mark.parametrize(
    "option_type",
    [
        OptionType.CALL,
        OptionType.PUT,
    ],
)
def test_gamma_matches_finite_difference(option_type: OptionType) -> None:
    step = 1e-2

    price_above = calculate_price(
        build_model(
            option_type,
            spot=SPOT + step,
        )
    )
    price_at_spot = calculate_price(
        build_model(
            option_type,
            spot=SPOT,
        )
    )
    price_below = calculate_price(
        build_model(
            option_type,
            spot=SPOT - step,
        )
    )

    numerical_gamma = (price_above - 2 * price_at_spot + price_below) / step**2

    analytical_gamma = BlackScholesGreeks(build_model(option_type)).gamma

    assert analytical_gamma == pytest.approx(
        numerical_gamma,
        rel=1e-5,
        abs=1e-7,
    )


@pytest.mark.parametrize(
    "option_type",
    [
        OptionType.CALL,
        OptionType.PUT,
    ],
)
def test_vega_matches_one_percentage_point_change(
    option_type: OptionType,
) -> None:
    step = 1e-4

    price_above = calculate_price(
        build_model(
            option_type,
            volatility=VOLATILITY + step,
        )
    )
    price_below = calculate_price(
        build_model(
            option_type,
            volatility=VOLATILITY - step,
        )
    )

    raw_vega = (price_above - price_below) / (2 * step)
    numerical_vega_per_percentage_point = raw_vega / 100

    analytical_vega = BlackScholesGreeks(build_model(option_type)).vega

    assert analytical_vega == pytest.approx(
        numerical_vega_per_percentage_point,
        rel=1e-6,
        abs=1e-8,
    )


@pytest.mark.parametrize(
    "option_type",
    [
        OptionType.CALL,
        OptionType.PUT,
    ],
)
def test_theta_matches_time_to_maturity_derivative(
    option_type: OptionType,
) -> None:
    step = 1e-4

    price_with_more_time = calculate_price(
        build_model(
            option_type,
            maturity=MATURITY + step,
        )
    )
    price_with_less_time = calculate_price(
        build_model(
            option_type,
            maturity=MATURITY - step,
        )
    )

    derivative_with_respect_to_maturity = (
        price_with_more_time - price_with_less_time
    ) / (2 * step)

    # Theta is minus the derivative with respect to time remaining,
    # converted from an annual value to a daily value.
    numerical_theta_per_day = -derivative_with_respect_to_maturity / 365

    analytical_theta = BlackScholesGreeks(build_model(option_type)).theta

    assert analytical_theta == pytest.approx(
        numerical_theta_per_day,
        rel=1e-6,
        abs=1e-8,
    )


@pytest.mark.parametrize(
    "option_type",
    [
        OptionType.CALL,
        OptionType.PUT,
    ],
)
def test_rho_matches_one_percentage_point_rate_change(
    option_type: OptionType,
) -> None:
    step = 1e-5

    price_above = calculate_price(
        build_model(
            option_type,
            risk_free_rate=RISK_FREE_RATE + step,
        )
    )
    price_below = calculate_price(
        build_model(
            option_type,
            risk_free_rate=RISK_FREE_RATE - step,
        )
    )

    raw_rho = (price_above - price_below) / (2 * step)
    numerical_rho_per_percentage_point = raw_rho / 100

    analytical_rho = BlackScholesGreeks(build_model(option_type)).rho

    assert analytical_rho == pytest.approx(
        numerical_rho_per_percentage_point,
        rel=1e-6,
        abs=1e-8,
    )
