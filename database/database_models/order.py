from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from database.engine import Base


class OrdersOrm(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(primary_key=True)
    status: Mapped[str]
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    direction: Mapped[str]
    ticker: Mapped[str]
    qty: Mapped[int]
