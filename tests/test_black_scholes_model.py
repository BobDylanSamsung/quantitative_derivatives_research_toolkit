from math import exp

import pytest

from derivative_pricing.models.market import MarketData
from derivative_pricing.models.options import EuropeanOption, OptionType
from derivative_pricing.pricing.black_scholes_model import BlackScholesModel


@pytest.fixture
def call_model() -> BlackScholesModel:
    market = MarketData(
        spot=100.0,
        risk_free_rate=0.05,
        volatility=0.20,
    )

    option = EuropeanOption(
        strike=100.0,
        maturity=1.0,
    )

    return BlackScholesModel(
        option=option,
        market=market,
    )


@pytest.fixture
def put_model() -> BlackScholesModel:
    market = MarketData(
        spot=100.0,
        risk_free_rate=0.05,
        volatility=0.20,
    )

    option = EuropeanOption(strike=100.0, maturity=1.0, type=OptionType.PUT)

    return BlackScholesModel(
        option=option,
        market=market,
    )


def test_call_price(call_model: BlackScholesModel) -> None:
    assert call_model.calculate_call() == pytest.approx(
        10.4506,
        abs=1e-4,
    )


def test_put_price(put_model: BlackScholesModel) -> None:
    assert put_model.calculate_put() == pytest.approx(
        5.5735,
        abs=1e-4,
    )


def test_put_call_parity(
    call_model: BlackScholesModel,
    put_model: BlackScholesModel,
) -> None:
    assert call_model.market == put_model.market
    assert call_model.option.strike == put_model.option.strike
    assert call_model.option.maturity == put_model.option.maturity

    call_price = call_model.calculate_call()
    put_price = put_model.calculate_put()

    discounted_strike = call_model.option.strike * exp(
        -call_model.market.risk_free_rate * call_model.option.maturity
    )

    expected_difference = call_model.market.spot - discounted_strike

    assert call_price - put_price == pytest.approx(
        expected_difference,
        abs=1e-10,
    )
