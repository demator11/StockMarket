import datetime
from uuid import UUID, uuid4

from sqlalchemy import FetchedValue, func
from sqlalchemy.orm import Mapped, mapped_column

from application.database.engine import Base


class OutboxMessageOrm(Base):
    __tablename__ = "outbox"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4, server_default=FetchedValue()
    )
    payload: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.now(), server_default=func.now()
    )
    is_sent: Mapped[bool] = mapped_column(
        default=False, server_default="False"
    )
