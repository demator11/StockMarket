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


POSTGRESQL_USER = os.getenv("POSTGRESQL_USER")
POSTGRESQL_HOST = os.getenv("POSTGRESQL_HOST")
POSTGRESQL_PORT = os.getenv("POSTGRESQL_PORT")
POSTGRESQL_PASS = os.getenv("POSTGRESQL_PASS")
POSTGRESQL_NAME = os.getenv("POSTGRESQL_NAME")


POSTGRESQL_URL = get_database_url(
    db_host=POSTGRESQL_HOST,
    db_port=POSTGRESQL_PORT,
    db_user=POSTGRESQL_USER,
    db_pass=POSTGRESQL_PASS,
    db_name=POSTGRESQL_NAME,
)

POSTGRESQL_ECHO = bool(os.getenv("POSTGRESQL_ECHO"))

JWT_SECRET_KEY = os.getenv("SECRET_KEY")
