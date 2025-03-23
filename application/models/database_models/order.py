from uuid import UUID, uuid4

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.schema import FetchedValue

from application.database.engine import Base
from application.models.enum_models.order import Direction, OrderStatus


class OrderOrm(Base):
    __tablename__ = "orders"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4, server_default=FetchedValue()
    )
    status: Mapped[OrderStatus]
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE")
    )
    direction: Mapped[Direction]
    ticker: Mapped[str]
    qty: Mapped[int]
    price: Mapped[int] = mapped_column(nullable=True)
    filled: Mapped[int] = mapped_column(default=0)
