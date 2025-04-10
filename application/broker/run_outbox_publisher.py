import asyncio

from application.broker.client import RabbitMQClient
from application.database.config import RABBITMQ_URL
from application.database.engine import async_session_factory
from application.database.repository.outbox_message_repository import (
    OutboxMessageRepository,
)
from application.models.database_models.order import Order


async def main() -> None:
    rabbit_client = RabbitMQClient(RABBITMQ_URL)
    await rabbit_client.connect()
    try:
        while True:
            async with async_session_factory.begin() as session:
                outbox_message_repository = OutboxMessageRepository(
                    db_session=session
                )
                messages = await outbox_message_repository.get(100)

                for message in messages:
                    try:
                        order = Order.model_validate_json(message.payload)
                        await rabbit_client.produce_order(order)
                        await outbox_message_repository.update_status(
                            message.id, True
                        )
                    except Exception as error:
                        # todo заменить на logger
                        print(error)

            await asyncio.sleep(1)
    finally:
        await rabbit_client.close()


if __name__ == "__main__":
    asyncio.run(main())
