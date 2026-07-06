import asyncio

from aio_pika import IncomingMessage

from application.broker.client import RabbitMQClient
from application.database.engine import async_session_factory
from application.database.repository.app_config_repository import (
    AppConfigRepository,
)
from application.database.repository.balance_repository import (
    BalanceRepository,
)
from application.database.repository.order_repository import OrderRepository
from application.database.repository.transaction_repository import (
    TransactionRepository,
)
from application.logger import setup_logging
from application.models.database_models.order import Order
from application.order_consumer import process_order

logger = setup_logging(__name__)


async def handle_message(message: IncomingMessage) -> None:
    current_order = Order.model_validate_json(message.body.decode())
    logger.info(f"Consumer received order {current_order.id}")

    async with async_session_factory.begin() as session:
        order_repository = OrderRepository(db_session=session)
        balance_repository = BalanceRepository(db_session=session)
        transaction_repository = TransactionRepository(db_session=session)
        app_config_repository = AppConfigRepository(db_session=session)

        result = await process_order(
            current_order=current_order,
            balance_repository=balance_repository,
            order_repository=order_repository,
            transaction_repository=transaction_repository,
            app_config_repository=app_config_repository,
        )

        await session.commit()

        if result.status_code != 200:
            logger.warning(
                f"Order {current_order.id} processed with "
                f"status {result.status_code}: {result.detail}"
            )
        else:
            logger.info(f"Order {current_order.id} processed successfully")

    await message.ack()


async def consume_orders() -> None:
    rabbit = RabbitMQClient()

    try:
        await rabbit.connect()
        logger.info("Broker (order consumer) started")
        await rabbit.consume(on_message=handle_message)
    finally:
        await rabbit.close()
        logger.info("Broker stopped")


def main() -> None:
    asyncio.run(consume_orders())


if __name__ == "__main__":
    main()
