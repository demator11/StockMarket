import pytest

from application.models.database_models.instrument import Instrument


@pytest.fixture
def instrument_list() -> list[Instrument]:
    return [
        Instrument(name="BITCOIN", ticker="BTC"),
        Instrument(name="Ethereum", ticker="ETH"),
    ]
