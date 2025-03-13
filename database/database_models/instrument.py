from uuid import UUID, uuid4
from sqlalchemy.orm import Mapped, mapped_column

from database.engine import Base


class InstrumentOrm(Base):
    __tablename__ = "instrument"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str]
    ticker: Mapped[str]
