from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class Direction(Enum):
    buy = "BUY"
    sell = "SELL"


class OrderStatus(Enum):
    new = "NEW"
    executed = "EXECUTED"
    partially_executed = "PARTIALLY_EXECUTED"
    cancelled = "CANCELLED"


class LimitOrderBody(BaseModel):
    direction: Direction
    ticker: str
    qry: int = Field(ge=1)
    price: int = Field(gt=0)


class LimitOrder(BaseModel):
    id: UUID
    status: OrderStatus
    user_id: UUID
    body: LimitOrderBody
    filled: int = 0


class CreateOrderResponse(BaseModel):
    success: bool = True
    order_id: int
