from alembic import command
from alembic.config import Config
from sqlalchemy import select, insert

from database.engine import async_engine, Base, async_session_factory
from database.database_models.user import UserOrm
from database.database_models.order import OrderOrm
from database.database_models.balance import BalanceOrm
from models.user import User, NewUser, UserRole


class AsyncORM:
    @staticmethod
    async def drop_tables():
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    @staticmethod
    async def create_tables():
        alembic_config = Config("alembic.ini")
        async with async_engine.begin() as conn:
            await conn.run_sync(
                lambda connection: command.upgrade(alembic_config, "head")
            )
            await conn.run_sync(Base.metadata.create_all)

    @staticmethod
    async def create_user(new_user: NewUser, api_key: str):
        async with async_session_factory() as session:
            result = await session.scalars(
                insert(UserOrm)
                .values(
                    name=new_user.name, role=UserRole.user, api_key=api_key
                )
                .returning(UserOrm)
            )
            return User.from_orm(result.one())

    @staticmethod
    async def check_has_in_database(user_name: str) -> bool:
        async with async_session_factory() as session:
            query = select(UserOrm.name).filter(UserOrm.name == user_name)
            result = await session.execute(query)
            if result.first() is None:
                return False
            return True
