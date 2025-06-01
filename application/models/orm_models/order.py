import datetime
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.schema import FetchedValue

from application.config import timestamp_utc
from application.database.engine import Base
from application.models.database_models.order import (
    OrderDirection,
    OrderStatus,
)


class OrderOrm(Base):
    __tablename__ = "orders"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4, server_default=FetchedValue()
    )
    status: Mapped[OrderStatus]
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
    )
    timestamp: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=timestamp_utc,
        server_default=func.now(),
        nullable=False,
    )
    direction: Mapped[OrderDirection]
    ticker: Mapped[str] = mapped_column(index=True)
    qty: Mapped[int]
    price: Mapped[int | None] = mapped_column(nullable=True)
    filled: Mapped[int] = mapped_column(default=0, server_default="0")
