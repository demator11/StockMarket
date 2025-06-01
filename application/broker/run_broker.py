import asyncio

from application.broker.client import RabbitMQClient
from application.config import RABBITMQ_URL
from logger import setup_logging

logger = setup_logging("rabbit_consumer")


async def main() -> None:
    logger.info("The consumer has started")
    rabbit_client = RabbitMQClient(RABBITMQ_URL)
    await rabbit_client.connect()
    try:
        await rabbit_client.consume()
    finally:
        logger.info("The consumer has stopped")
        await rabbit_client.close()


if __name__ == "__main__":
    asyncio.run(main())
