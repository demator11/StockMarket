from uuid import UUID

from pydantic import Field

from models.endpoints_models.base import ModelBase
from models.enum_models.order import Direction, OrderStatus


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
