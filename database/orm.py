from alembic import command
from alembic.config import Config

from database.engine import async_engine, Base, async_session_factory
from database.database_models.user import UserOrm
from database.database_models.order import OrderOrm
from database.database_models.balance import BalanceOrm
from database.database_models.instrument import InstrumentOrm
from models.user import User, NewUser, UserRole


class AsyncORM:
    @staticmethod
    async def migration():
        alembic_config = Config("alembic.ini")
        async with async_engine.begin() as conn:
            await conn.run_sync(
                lambda connection: command.downgrade(alembic_config, "base")
            )
        async with async_engine.begin() as conn:
            await conn.run_sync(
                lambda connection: command.upgrade(alembic_config, "head")
            )
