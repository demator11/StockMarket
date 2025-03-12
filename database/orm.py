from database.engine import async_engine, Base
from database.database_models.user import UserOrm
from database.database_models.order import OrdersOrm
from database.database_models.balance import BalanceOrm


class AsyncORM:
    @staticmethod
    async def create_tables():
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
