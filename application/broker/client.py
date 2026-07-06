import asyncio

import aio_pika
from aio_pika.abc import AbstractRobustConnection

from application.config import RABBITMQ_URL
from application.logger import setup_logging

logger = setup_logging(__name__)

CONNECT_RETRY_DELAY = 0.5
CONNECT_MAX_RETRIES = 12


class RabbitMQClient:
    def __init__(self, queue: str = "orders"):
        self.queue = queue
        self._connection: AbstractRobustConnection | None = None

    async def connect(self) -> None:
        last_exc = None
        for attempt in range(1, CONNECT_MAX_RETRIES + 1):
            try:
                self._connection = await aio_pika.connect_robust(RABBITMQ_URL)
                logger.info("Connected to RabbitMQ")
                return
            except Exception as exc:
                last_exc = exc
                logger.warning(
                    f"RabbitMQ connection attempt {attempt}/"
                    f"{CONNECT_MAX_RETRIES} failed, retrying in "
                    f"{CONNECT_RETRY_DELAY}s"
                )
                await asyncio.sleep(CONNECT_RETRY_DELAY)

        raise ConnectionError(
            f"Could not connect to RabbitMQ after "
            f"{CONNECT_MAX_RETRIES} attempts"
        ) from last_exc

    async def close(self) -> None:
        if self._connection and not self._connection.is_closed:
            await self._connection.close()
            logger.info("RabbitMQ connection closed")

    async def publish(
        self, payload: str, routing_key: str | None = None
    ) -> None:
        if not self._connection:
            raise RuntimeError("RabbitMQClient is not connected")

        async with self._connection.channel() as channel:
            queue = await channel.declare_queue(self.queue, durable=True)
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=payload.encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                ),
                routing_key=routing_key or queue.name,
            )
            logger.debug(f"Published message to queue '{self.queue}'")

    async def consume(
        self,
        on_message,
        prefetch_count: int = 1,
    ) -> None:
        if not self._connection:
            raise RuntimeError("RabbitMQClient is not connected")

        async with self._connection.channel() as channel:
            await channel.set_qos(prefetch_count=prefetch_count)
            queue = await channel.declare_queue(self.queue, durable=True)

            logger.info(
                f"Consumer started, waiting for messages on '{self.queue}'"
            )

            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process(ignore_processed=True):
                        try:
                            await on_message(message)
                        except Exception:
                            logger.exception(
                                f"Failed to process message "
                                f"{message.message_id}"
                            )
                            await message.reject(requeue=True)
