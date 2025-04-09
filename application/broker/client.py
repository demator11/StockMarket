import aio_pika
from aio_pika.abc import AbstractRobustConnection

from application.broker.order_consumer import process_order
from application.database.repository.order_repository import OrderRepository
from application.models.database_models.order import Order


class RabbitMQClient:
    def __init__(
        self, connection: AbstractRobustConnection, queue: str = "orders"
    ):
        self.connection = connection
        self.queue = queue

    async def produce_order(
        self,
        order: Order,
    ) -> None:
        async with self.connection:
            async with await self.connection.channel() as channel:
                queue = await channel.declare_queue(self.queue, durable=True)
                await channel.default_exchange.publish(
                    aio_pika.Message(body=order.json().encode()),
                    routing_key=queue.name,
                )

    async def consume(self) -> None:
        async with self.connection:
            async with await self.connection.channel() as channel:
                queue = await channel.declare_queue(self.queue, durable=True)
                async with queue.iterator() as queue_iter:
                    async for message in queue_iter:
                        await process_order(message)
