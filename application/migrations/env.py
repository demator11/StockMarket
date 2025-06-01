from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from application.config import POSTGRESQL_URL
from application.models.orm_models.user import UserOrm  # noqa
from application.models.orm_models.balance import BalanceOrm  # noqa
from application.models.orm_models.order import OrderOrm  # noqa
from application.models.orm_models.instrument import InstrumentOrm  # noqa
from application.models.orm_models.transaction import TransactionOrm  # noqa
from application.models.orm_models.outbox_message import (  # noqa
    OutboxMessageOrm,
)
from application.models.orm_models.app_config import AppConfigOrm  # noqa
from application.database.engine import Base

config = context.config


if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option(
    "sqlalchemy.url", POSTGRESQL_URL + "?async_fallback=True"
)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
