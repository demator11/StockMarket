import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from application.database.engine import Base


class AppConfigOrm(Base):
    __tablename__ = "config"

    key: Mapped[str] = mapped_column(
        primary_key=True,
    )
    value: Mapped[str]
    updated_at: Mapped[datetime.datetime] = mapped_column(
        default=datetime.datetime.now(), server_default=func.now()
    )
