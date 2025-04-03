from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.schema import FetchedValue

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
    direction: Mapped[OrderDirection]
    ticker: Mapped[str] = mapped_column(index=True)
    qty: Mapped[int]
    price: Mapped[int | None] = mapped_column(nullable=True)
    filled: Mapped[int] = mapped_column(default=0, server_default="0")
