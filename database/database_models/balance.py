from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from database.engine import Base


class BalanceOrm(Base):
    __tablename__ = "balances"

    id: Mapped[str] = mapped_column(primary_key=True)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    currency: Mapped[str]
    qty: Mapped[int]
