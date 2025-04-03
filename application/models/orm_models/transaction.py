import datetime
from uuid import UUID, uuid4

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.schema import FetchedValue

from application.database.engine import Base


class TransactionOrm(Base):
    __tablename__ = "transaction"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4, server_default=FetchedValue()
    )
    ticker: Mapped[str] = mapped_column(index=True)
    qty: Mapped[int]
    price: Mapped[int]
    timestamp: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.now(), server_default=func.now()
    )
