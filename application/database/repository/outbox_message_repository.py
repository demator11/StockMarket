from datetime import datetime, timedelta
from uuid import UUID

from sqlalchemy import insert, select, update, delete, or_
from sqlalchemy.ext.asyncio import AsyncSession

from application.models.database_models.outbox_message import OutboxMessage
from application.models.orm_models.outbox_message import OutboxMessageOrm


class OutboxMessageRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(self, message: OutboxMessage):
        await self.db_session.execute(
            insert(OutboxMessageOrm).values(
                id=message.id,
                payload=message.payload,
            )
        )

    async def get(self, limit: int = 100):
        result = await self.db_session.scalars(
            select(OutboxMessageOrm)
            .where(
                or_(
                    OutboxMessageOrm.is_sent.is_(False),
                    OutboxMessageOrm.created_at
                    < datetime.now() - timedelta(minutes=5),
                )
            )
            .limit(limit)
        )
        return [
            OutboxMessage.model_validate(message) for message in result.all()
        ]

    async def update_status(self, message_id: UUID, status: bool):
        await self.db_session.execute(
            update(OutboxMessageOrm)
            .where(OutboxMessageOrm.id == message_id)
            .values(is_sent=status)
        )

    async def delete(self, message_id):
        await self.db_session.execute(
            delete(OutboxMessageOrm).where(OutboxMessageOrm.id == message_id)
        )
