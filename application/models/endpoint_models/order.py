from uuid import UUID

from pydantic import Field, BaseModel

from application.models.enum_models.order import OrderDirection, OrderStatus


class CreateOrderBodyRequest(BaseModel):
    direction: OrderDirection
    ticker: str = Field(pattern=r"^[A-Z]{2,10}$")
    qty: int = Field(ge=1)
    price: int = Field(gt=0, default=None)


class LimitOrderBodyRequest(BaseModel):
    direction: OrderDirection
    ticker: str = Field(pattern=r"^[A-Z]{2,10}$")
    qty: int = Field(ge=1)
    price: int = Field(gt=0)


class LimitOrderBodyResponse(BaseModel):
    direction: OrderDirection
    ticker: str = Field(pattern=r"^[A-Z]{2,10}$")
    qty: int = Field(ge=1)
    price: int = Field(gt=0)


class LimitOrderResponse(BaseModel):
    id: UUID
    status: OrderStatus
    user_id: UUID
    body: LimitOrderBodyRequest
    filled: int = 0


class MarketOrderBodyRequest(BaseModel):
    direction: OrderDirection
    ticker: str = Field(pattern=r"^[A-Z]{2,10}$")
    qty: int = Field(ge=1)


class MarketOrderBodyResponse(BaseModel):
    direction: OrderDirection
    ticker: str = Field(pattern=r"^[A-Z]{2,10}$")
    qty: int = Field(ge=1)


class MarketOrderResponse(BaseModel):
    id: UUID
    status: OrderStatus
    user_id: UUID
    body: MarketOrderBodyRequest


class CreateOrderResponse(BaseModel):
    success: bool = True
    order_id: UUID
