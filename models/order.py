from enum import Enum
from uuid import UUID
from typing import Literal, Union

from pydantic import Field

from models.base import ModelBase


class Direction(Enum):
    buy = "BUY"
    sell = "SELL"


class OrderStatus(Enum):
    new = "NEW"
    executed = "EXECUTED"
    partially_executed = "PARTIALLY_EXECUTED"
    cancelled = "CANCELLED"


class LimitOrderBody(ModelBase):
    direction: Direction
    ticker: str = Field(pattern=r"^[A-Z]{2,10}$")
    qty: int = Field(ge=1)
    price: int = Field(gt=0)


class LimitOrder(ModelBase):
    id: UUID
    status: OrderStatus
    user_id: UUID
    body: LimitOrderBody
    filled: int = 0


class MarketOrderBody(ModelBase):
    direction: Direction
    ticker: str = Field(pattern=r"^[A-Z]{2,10}$")
    qty: int = Field(ge=1)


class MarketOrder(ModelBase):
    id: UUID
    status: OrderStatus
    user_id: UUID
    body: MarketOrderBody


class RawOrderBody:
    direction: Direction
    ticker: str = Field(pattern=r"^[A-Z]{2,10}$")
    qty: int = Field(ge=1)
    price: int = Field(gt=0)


class RawOrder(ModelBase):
    id: UUID
    order_type: str
    status: OrderStatus
    user_id: UUID
    direction: Direction
    ticker: str = Field(pattern=r"^[A-Z]{2,10}$")
    qty: int
    price: int | None
    filled: int = 0


class CreateOrderResponse(ModelBase):
    success: bool = True
    order_id: UUID
