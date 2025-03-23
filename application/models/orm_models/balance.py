from uuid import UUID, uuid4
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.schema import FetchedValue

from application.database.engine import Base


class BalanceOrm(Base):
    __tablename__ = "balances"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4, server_default=FetchedValue()
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
    )
    ticker: Mapped[str] = mapped_column(index=True)
    qty: Mapped[int]
