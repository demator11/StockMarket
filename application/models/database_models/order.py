import uuid
from enum import StrEnum
from uuid import UUID

from pydantic import Field

from application.models.base import ModelBase


class OrderDirection(StrEnum):
    buy = "BUY"
    sell = "SELL"


class OrderStatus(StrEnum):
    new = "NEW"
    executed = "EXECUTED"
    partially_executed = "PARTIALLY_EXECUTED"
    cancelled = "CANCELLED"


class UpdateOrder(ModelBase):
    id: UUID
    status: OrderStatus | None = None
    user_id: UUID | None = None
    direction: OrderDirection | None = None
    ticker: str | None = None
    qty: int | None = None
    price: int | None = None
    filled: int | None = None


class Order(ModelBase):
    id: UUID = Field(default_factory=uuid.uuid4)
    status: OrderStatus
    user_id: UUID
    direction: OrderDirection
    ticker: str
    qty: int
    price: int | None
    filled: int = 0
