import asyncio

import aio_pika

from application.broker.client import RabbitMQClient
from application.database.config import RABBITMQ_URL
from application.database.engine import async_session_factory
from application.database.repository.order_repository import OrderRepository


async def main() -> None:
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    rabbit_client = RabbitMQClient(connection=connection)
    await rabbit_client.consume()


if __name__ == "__main__":
    asyncio.run(main())
