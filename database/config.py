import os

from dotenv import load_dotenv

load_dotenv()


def get_database_url(
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


POSTGRESQL_URL = get_database_url(
    db_host=POSTGRESQL_HOST,
    db_port=POSTGRESQL_PORT,
    db_user=POSTGRESQL_USER,
    db_pass=POSTGRESQL_PASS,
    db_name=POSTGRESQL_NAME,
)

POSTGRES_ECHO = bool(os.getenv("POSTGRES_ECHO"))

JWT_SECRET_KEY = os.getenv("SECRET_KEY")
JWT_ALGORITHM = os.getenv("ALGORITHM")
