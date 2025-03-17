from uuid import UUID

from pydantic import Field

from models.base import ModelBase
from models.enum_models.order import Direction, OrderStatus


class LimitOrderBodyRequest(ModelBase):
    direction: Direction
    ticker: str = Field(pattern=r"^[A-Z]{2,10}$")
    qty: int = Field(ge=1)
    price: int = Field(gt=0)


class LimitOrderBodyResponse(ModelBase):
    direction: Direction
    ticker: str = Field(pattern=r"^[A-Z]{2,10}$")
    qty: int = Field(ge=1)
    price: int = Field(gt=0)


class LimitOrderResponse(ModelBase):
    id: UUID
    status: OrderStatus
    user_id: UUID
    body: LimitOrderBodyRequest
    filled: int = 0


class MarketOrderBodyRequest(ModelBase):
    direction: Direction
    ticker: str = Field(pattern=r"^[A-Z]{2,10}$")
    qty: int = Field(ge=1)


class MarketOrderBodyResponse(ModelBase):
    direction: Direction
    ticker: str = Field(pattern=r"^[A-Z]{2,10}$")
    qty: int = Field(ge=1)


class MarketOrderResponse(ModelBase):
    id: UUID
    status: OrderStatus
    user_id: UUID
    body: MarketOrderBodyRequest


class CreateOrderResponse(ModelBase):
    success: bool = True
    order_id: UUID
