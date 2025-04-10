import asyncio

from application.broker.client import RabbitMQClient
from application.database.config import RABBITMQ_URL


async def main() -> None:
    rabbit_client = RabbitMQClient(RABBITMQ_URL)
    await rabbit_client.connect()
    try:
        await rabbit_client.consume()
    finally:
        await rabbit_client.close()


if __name__ == "__main__":
    asyncio.run(main())
