from uuid import UUID, uuid4
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.schema import FetchedValue

from application.database.engine import Base


class UserOrm(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4, server_default=FetchedValue()
    )
    name: Mapped[str] = mapped_column(unique=True)
    role: Mapped[str] = mapped_column(default="USER", server_default="USER")
    api_key: Mapped[str]
