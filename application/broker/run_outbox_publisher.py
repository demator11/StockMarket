import asyncio

from application.broker.client import RabbitMQClient
from application.database.engine import async_session_factory
from application.database.repository.outbox_message_repository import (
    OutboxMessageRepository,
)
from application.logger import setup_logging

logger = setup_logging(__name__)

POLL_INTERVAL_SECONDS = 2
BATCH_SIZE = 50


async def publish_outbox_messages() -> None:
    rabbit = RabbitMQClient()

    try:
        await rabbit.connect()
        logger.info("Outbox publisher started")

        while True:
            async with async_session_factory.begin() as session:
                repository = OutboxMessageRepository(db_session=session)
                messages = await repository.get(limit=BATCH_SIZE)

                for msg in messages:
                    try:
                        await rabbit.publish(payload=msg.payload)
                        await repository.update_status(
                            message_id=msg.id, status=True
                        )
                        logger.debug(
                            f"Published and marked outbox message {msg.id}"
                        )
                    except Exception:
                        logger.exception(
                            f"Failed to publish outbox message {msg.id}"
                        )

                if messages:
                    await session.commit()

            await asyncio.sleep(POLL_INTERVAL_SECONDS)

    finally:
        await rabbit.close()
        logger.info("Outbox publisher stopped")


def main() -> None:
    asyncio.run(publish_outbox_messages())


if __name__ == "__main__":
    main()
