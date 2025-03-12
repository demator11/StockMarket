import os
from dotenv import load_dotenv

load_dotenv()


def DATABASE_URL_asyncpg(
    db_host: str, db_port: str, db_user: str, db_pass: str, db_name: str
) -> str:
    return (
        f"postgresql+asyncpg://"
        f"{db_user}:{db_pass}@{db_host}:"
        f"{db_port}/{db_name}"
    )


POSTGRESQL_USER = os.getenv("DB_USER")
POSTGRESQL_HOST = os.getenv("DB_HOST")
POSTGRESQL_PORT = os.getenv("DB_PORT")
POSTGRESQL_PASS = os.getenv("DB_PASS")
POSTGRESQL_NAME = os.getenv("DB_NAME")


POSTGRESQL_URL = DATABASE_URL_asyncpg(
    POSTGRESQL_HOST,
    POSTGRESQL_PORT,
    POSTGRESQL_USER,
    POSTGRESQL_PASS,
    POSTGRESQL_NAME,
)
