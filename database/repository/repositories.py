from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import async_session_factory
from database.repository.user_repository import UserRepository
from database.repository.instrument_repository import InstrumentRepository
from database.repository.balance_repository import BalanceRepository
from database.repository.order_repository import OrderRepository


async def get_db() -> AsyncSession:
    async with async_session_factory.begin() as session:
        yield session


def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db_session=db)


def get_instrument_repository(
    db: AsyncSession = Depends(get_db),
) -> InstrumentRepository:
    return InstrumentRepository(db_session=db)


def get_balance_repository(
    db: AsyncSession = Depends(get_db),
) -> BalanceRepository:
    return BalanceRepository(db_session=db)


def get_order_repository(
    db: AsyncSession = Depends(get_db),
) -> OrderRepository:
    return OrderRepository(db_session=db)
