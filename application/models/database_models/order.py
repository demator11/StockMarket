from uuid import UUID

from pydantic import Field

from application.models.base import ModelBase
from application.models.enum_models.order import OrderDirection, OrderStatus


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
    id: UUID
    status: OrderStatus
    user_id: UUID
    direction: OrderDirection
    ticker: str
    qty: int
    price: int | None
    filled: int = 0


class OrderBody(ModelBase):
    direction: OrderDirection
    ticker: str = Field(pattern=r"^[A-Z]{2,10}$")
    qty: int = Field(ge=1)
    price: int = Field(gt=0, default=None)
