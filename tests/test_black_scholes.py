from math import exp

import pytest

from derivative_pricing.models.market import MarketData
from derivative_pricing.models.options import EuropeanOption
from derivative_pricing.pricing.black_scholes import BlackScholes


@pytest.fixture
def model() -> BlackScholes:
    market = MarketData(
        spot=100.0,
        risk_free_rate=0.05,
        volatility=0.20,
    )

    option = EuropeanOption(
        strike=100.0,
        maturity=1.0,
    )

    return BlackScholes(
        option=option,
        market=market,
    )


def test_call_price(model: BlackScholes) -> None:
    assert model.calculate_call() == pytest.approx(
        10.4506,
        abs=1e-4,
    )


def test_put_price(model: BlackScholes) -> None:
    assert model.calculate_put() == pytest.approx(
        5.5735,
        abs=1e-4,
    )


def test_put_call_parity(model: BlackScholes) -> None:
    call_price = model.calculate_call()
    put_price = model.calculate_put()

    discounted_strike = model.option.strike * exp(
        -model.market.risk_free_rate * model.option.maturity
    )

    assert call_price - put_price == pytest.approx(
        model.market.spot - discounted_strike,
        abs=1e-10,
    )
