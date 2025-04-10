import aio_pika

from application.broker.order_consumer import process_order
from application.models.database_models.order import Order


class RabbitMQClient:
    def __init__(self, connection_url: str, queue: str = "orders"):
        self.connection_url = connection_url
        self.queue = queue
        self.connection = None
        self.channel = None

    async def connect(self):
        self.connection = await aio_pika.connect_robust(self.connection_url)
        self.channel = await self.connection.channel()

    async def close(self):
        if self.connection:
            await self.connection.close()

    async def produce_order(
        self,
        order: Order,
    ) -> None:
        if self.channel:
            queue = await self.channel.declare_queue(self.queue, durable=True)
            await self.channel.default_exchange.publish(
                aio_pika.Message(body=order.json().encode()),
                routing_key=queue.name,
            )

    async def consume(self) -> None:
        if self.channel:
            queue = await self.channel.declare_queue(self.queue, durable=True)
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    await process_order(message)
