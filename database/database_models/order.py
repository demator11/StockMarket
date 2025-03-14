from uuid import UUID, uuid4
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from database.engine import Base
from models.order import Direction, OrderStatus


class OrderOrm(Base):
    __tablename__ = "orders"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    order_type: Mapped[str]
    status: Mapped[OrderStatus]
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    direction: Mapped[Direction]
    ticker: Mapped[str]
    qty: Mapped[int]
    price: Mapped[int] = mapped_column(nullable=True)
    filled: Mapped[int] = mapped_column(default=0)
