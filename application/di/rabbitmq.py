import aio_pika
from aio_pika.abc import AbstractRobustConnection
from fastapi import Depends

from application.broker.client import RabbitMQClient
from application.database.config import RABBITMQ_URL


async def get_rabbitmq_connection() -> AbstractRobustConnection:
    return await aio_pika.connect_robust(RABBITMQ_URL)


def get_rabbitmq_client(
    connect: AbstractRobustConnection = Depends(get_rabbitmq_connection),
) -> RabbitMQClient:
    return RabbitMQClient(connection=connect)
