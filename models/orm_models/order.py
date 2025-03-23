from uuid import UUID

from pydantic import Field

from models.base import ModelBase
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


class UpdateOrder(ModelBase):
    id: UUID
    status: OrderStatus | None = None
    user_id: UUID | None = None
    direction: Direction | None = None
    ticker: str | None = None
    qty: int | None = None
    price: int | None = None
    filled: int | None = None


class Order(ModelBase):
    id: UUID
    status: OrderStatus
    user_id: UUID
    direction: Direction
    ticker: str = Field(pattern=r"^[A-Z]{2,10}$")
    qty: int
    price: int | None
    filled: int = 0


class OrderBody(ModelBase):
    direction: Direction
    ticker: str = Field(pattern=r"^[A-Z]{2,10}$")
    qty: int = Field(ge=1)
    price: int = Field(gt=0, default=None)
