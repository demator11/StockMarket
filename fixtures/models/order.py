import uuid

import pytest

from application.models.database_models.order import (
    Order,
    OrderStatus,
    OrderDirection,
)


@pytest.fixture()
def order_list() -> list[Order]:
    return [
        Order(
            id=uuid.uuid4(),
            status=OrderStatus.new,
            user_id=uuid.uuid4(),
            direction=OrderDirection.sell,
            ticker="BTC",
            qty=100,
            price=2000,
        ),
        Order(
            id=uuid.uuid4(),
            status=OrderStatus.new,
            user_id=uuid.uuid4(),
            direction=OrderDirection.buy,
            ticker="BTC",
            qty=100,
            price=2000,
        ),
    ]
