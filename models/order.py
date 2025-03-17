from uuid import UUID

from pydantic import Field

from models.endpoints_models.base import BaseModel
from models.enum_models.order import Direction, OrderStatus


class Order(BaseModel):
    id: UUID
    order_type: str
    status: OrderStatus
    user_id: UUID
    direction: Direction
    ticker: str = Field(pattern=r"^[A-Z]{2,10}$")
    qty: int
    price: int | None
    filled: int = 0
