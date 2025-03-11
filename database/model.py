from sqlalchemy.orm import Mapped, mapped_column
from database.engine import Base
from models.user import UserRole


class UserOrm(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    role: Mapped[UserRole]
    api_key: Mapped[str]
