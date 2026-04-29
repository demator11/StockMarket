from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from application.config import POSTGRESQL_ECHO, POSTGRESQL_URL

async_engine = create_async_engine(
    url=POSTGRESQL_URL,
    echo=POSTGRESQL_ECHO,
)


async_session_factory = async_sessionmaker(async_engine)


class Base(DeclarativeBase):
    pass
