from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.engine import async_session_factory
from database.repository.user_repository import UserRepository


async def get_db() -> AsyncSession:
    async with async_session_factory.begin() as session:
        yield session


def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db_session=db)
