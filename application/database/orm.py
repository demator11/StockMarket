from alembic import command
from alembic.config import Config

from application.database.engine import async_engine


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
