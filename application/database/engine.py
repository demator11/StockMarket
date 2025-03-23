from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from application.database.config import POSTGRESQL_URL, POSTGRESQL_ECHO

load_dotenv()

async_engine = create_async_engine(
    url=POSTGRESQL_URL,
    echo=POSTGRESQL_ECHO,
)


async_session_factory = async_sessionmaker(async_engine)


class Base(DeclarativeBase):
    pass
