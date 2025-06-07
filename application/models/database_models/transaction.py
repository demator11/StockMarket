import uuid
from datetime import datetime
from uuid import UUID

from pydantic import Field

from application.config import timestamp_utc
from application.models.base import ModelBase


class Transaction(ModelBase):
    id: UUID = Field(default_factory=uuid.uuid4)
    ticker: str
    qty: int
    price: int
    timestamp: datetime = Field(default_factory=timestamp_utc)
