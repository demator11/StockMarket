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


POSTGRESQL_USER = os.getenv("POSTGRESQL_USER", "postgres")
POSTGRESQL_HOST = os.getenv("POSTGRESQL_HOST", "127.0.0.1")
POSTGRESQL_PORT = os.getenv("POSTGRESQL_PORT", "5432")
POSTGRESQL_PASS = os.getenv("POSTGRESQL_PASS", "postgres")
POSTGRESQL_NAME = os.getenv("POSTGRESQL_NAME", "market")


POSTGRESQL_URL = get_database_url(
    db_host=POSTGRESQL_HOST,
    db_port=POSTGRESQL_PORT,
    db_user=POSTGRESQL_USER,
    db_pass=POSTGRESQL_PASS,
    db_name=POSTGRESQL_NAME,
)

POSTGRESQL_ECHO = bool(os.getenv("POSTGRESQL_ECHO"))


def get_rabbitmq_url(
    mq_host: str,
    mq_port: str,
    mq_login: str,
    mq_pass: str,
) -> str:
    return f"amqp://{mq_login}:{mq_pass}@{mq_host}:{mq_port}/"


RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", "5672")
RABBITMQ_LOGIN = os.getenv("RABBITMQ_LOGIN", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")

RABBITMQ_URL = get_rabbitmq_url(
    mq_host=RABBITMQ_HOST,
    mq_port=RABBITMQ_PORT,
    mq_login=RABBITMQ_LOGIN,
    mq_pass=RABBITMQ_PASS,
)

JWT_SECRET_KEY = os.getenv("SECRET_KEY")
