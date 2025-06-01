import os
from typing import Generator, AsyncGenerator

import asyncpg
import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from application.config import (
    POSTGRESQL_PASS,
    POSTGRESQL_HOST,
    POSTGRESQL_USER,
    POSTGRESQL_PORT,
    POSTGRESQL_NAME,
)
from application.database.engine import async_engine, async_session_factory


os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session")
def db_name() -> str:
    return POSTGRESQL_NAME


@pytest_asyncio.fixture(scope="session")
async def engine(db_name: str) -> AsyncGenerator[AsyncEngine, None]:
    cursor = await asyncpg.connect(
        password=POSTGRESQL_PASS,
        host=POSTGRESQL_HOST,
        user=POSTGRESQL_USER,
        port=POSTGRESQL_PORT,
    )

    try:
        await cursor.execute(f"CREATE DATABASE {db_name}")
    except Exception:
        await cursor.execute(
            f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{db_name}'
                  AND pid <> pg_backend_pid()
            """
        )
        await cursor.execute(f"DROP DATABASE {db_name}")
        await cursor.execute(f"CREATE DATABASE {db_name}")

    yield async_engine

    await cursor.execute(
        f"""
        SELECT pg_terminate_backend(pg_stat_activity.pid)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = '{db_name}'
          AND pid <> pg_backend_pid()
    """
    )
    # await async_engine.dispose()
    await cursor.execute(f"DROP DATABASE {db_name}")
    await cursor.close()


@pytest.fixture(scope="session")
def migration(engine: AsyncEngine) -> Generator[None, None, None]:
    alembic_config = Config("alembic.ini")
    command.upgrade(alembic_config, "head")
    yield
    command.downgrade(alembic_config, "base")


@pytest_asyncio.fixture(scope="module")
async def db_session(migration) -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        async with session.begin():
            print("Отдал сессию")
            yield session
            print("Закрыл сессию")
