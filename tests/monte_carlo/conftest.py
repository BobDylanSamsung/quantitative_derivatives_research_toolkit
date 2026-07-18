import pytest

from derivative_pricing.models.market import MarketData
from derivative_pricing.models.options import EuropeanOption, OptionType
from derivative_pricing.pricing.monte_carlo_model import MonteCarloModel


@pytest.fixture
def market() -> MarketData:
    return MarketData(
        spot=100.0,
        risk_free_rate=0.05,
        volatility=0.20,
    )


@pytest.fixture
def call_option() -> EuropeanOption:
    return EuropeanOption(
        strike=105.0,
        maturity=1.0,
        type=OptionType.CALL,
    )


@pytest.fixture
def put_option() -> EuropeanOption:
    return EuropeanOption(
        strike=105.0,
        maturity=1.0,
        type=OptionType.PUT,
    )


@pytest.fixture
def call_model(
    market: MarketData,
    call_option: EuropeanOption,
) -> MonteCarloModel:
    return MonteCarloModel(
        option=call_option,
        market=market,
        simulations=10_000,
        seed=42,
    )
