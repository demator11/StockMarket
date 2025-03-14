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
    ticker: str
    qty: int = Field(ge=1)
    price: int = Field(gt=0)


class LimitOrder(ModelBase):
    id: UUID
    order_type: Literal["limit"]
    status: OrderStatus
    user_id: UUID
    body: LimitOrderBody
    filled: int = 0


class MarketOrderBody(ModelBase):
    direction: Direction
    ticker: str
    qty: int = Field(ge=1)


class MarketOrder(ModelBase):
    id: UUID
    order_type: Literal["market"]
    status: OrderStatus
    user_id: UUID
    body: MarketOrderBody


class RawOrder(ModelBase):
    id: UUID
    status: OrderStatus
    user_id: UUID
    direction: Direction
    ticker: str
    qty: int = Field(ge=1)
    price: int = Field(gt=0)
    filled: int = 0


class CreateOrderResponse(ModelBase):
    success: bool = True
    order_id: UUID


class OrderModel(ModelBase):
    order: Union[MarketOrder, LimitOrder] = Field(discriminator="order_type")
