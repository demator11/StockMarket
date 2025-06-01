import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from application.database.repository.instrument_repository import (
    InstrumentRepository,
)
from application.database.repository.order_repository import OrderRepository


@pytest.fixture()
def instrument_repository(
    db_session: AsyncSession,
) -> InstrumentRepository:
    return InstrumentRepository(db_session=db_session)


@pytest.fixture()
def order_repository(
    db_session: AsyncSession,
) -> OrderRepository:
    return OrderRepository(db_session=db_session)
