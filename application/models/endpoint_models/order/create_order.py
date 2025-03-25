from uuid import UUID

from pydantic import BaseModel, Field

from application.models.database_models.order import OrderDirection


class CreateOrderRequest(BaseModel):
    direction: OrderDirection
    ticker: str = Field(pattern=r"^[A-Z]{2,10}$")
    qty: int = Field(ge=1)
    price: int = Field(gt=0, default=None)


class CreateOrderResponse(BaseModel):
    success: bool = True
    order_id: UUID
