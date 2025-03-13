import os
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from database.config import POSTGRESQL_URL, echo

load_dotenv()

async_engine = create_async_engine(
    url=POSTGRESQL_URL,
    echo=echo,
)


async_session_factory = async_sessionmaker(async_engine)


class Base(DeclarativeBase):
    pass
