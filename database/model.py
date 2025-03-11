from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from database.engine import Base
from models.user import UserRole
from models.order import OrderStatus, Direction


class UserOrm(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    role: Mapped[UserRole]
    api_key: Mapped[str]


class OrdersOrm(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(primary_key=True)
    status: Mapped[OrderStatus]
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    direction: Mapped[Direction]
    ticker: Mapped[str]
    qty: Mapped[int]


class BalancesOrm(Base):
    __tablename__ = "balances"

    id: Mapped[str] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    currency: Mapped[str]
    qty: Mapped[int]
