from functools import partial

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from application.database.engine import async_session_factory
from application.database.repository.app_config_repository import (
    AppConfigRepository,
)
from application.database.repository.outbox_message_repository import (
    OutboxMessageRepository,
)
from application.database.repository.transaction_repository import (
    TransactionRepository,
)
from application.database.repository.user_repository import UserRepository
from application.database.repository.instrument_repository import (
    InstrumentRepository,
)
from application.database.repository.balance_repository import (
    BalanceRepository,
)
from application.database.repository.order_repository import OrderRepository


async def get_db() -> AsyncSession:
    async with async_session_factory.begin() as session:
        yield session


def get_repository(repository_class):
    return partial(repository_class, db_session=Depends(get_db))


get_user_repository = get_repository(UserRepository)
get_instrument_repository = get_repository(InstrumentRepository)
get_balance_repository = get_repository(BalanceRepository)
get_order_repository = get_repository(OrderRepository)
get_transaction_repository = get_repository(TransactionRepository)
get_outbox_message_repository = get_repository(OutboxMessageRepository)
get_app_config_repository = get_repository(AppConfigRepository)
