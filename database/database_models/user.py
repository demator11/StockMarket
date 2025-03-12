from uuid import UUID, uuid4
from sqlalchemy.orm import Mapped, mapped_column

from database.engine import Base


class UserOrm(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str]
    role: Mapped[str]
    api_key: Mapped[str]
