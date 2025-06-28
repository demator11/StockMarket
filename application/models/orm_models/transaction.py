import datetime
from uuid import UUID, uuid4

from sqlalchemy import func, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.schema import FetchedValue

from application.config import timestamp_utc
from application.database.engine import Base


class TransactionOrm(Base):
    __tablename__ = "transaction"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4, server_default=FetchedValue()
    )
    ticker: Mapped[str] = mapped_column(
        ForeignKey(
            "instrument.ticker", ondelete="CASCADE", onupdate="CASCADE"
        ),
        index=True,
    )
    qty: Mapped[int]
    price: Mapped[int]
    timestamp: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        default=timestamp_utc,
        server_default=func.now(),
        nullable=False,
    )
