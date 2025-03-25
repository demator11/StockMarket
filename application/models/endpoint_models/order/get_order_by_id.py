from uuid import UUID

from pydantic import Field, BaseModel

from application.models.database_models.order import (
    OrderDirection,
    OrderStatus,
)


class LimitOrderBodyByIdResponse(BaseModel):
    direction: OrderDirection
    ticker: str = Field(pattern=r"^[A-Z]{2,10}$")
    qty: int = Field(ge=1)
    price: int = Field(gt=0)


class LimitOrderByIdResponse(BaseModel):
    id: UUID
    status: OrderStatus
    user_id: UUID
    body: LimitOrderBodyByIdResponse
    filled: int = 0


class MarketOrderBodyByIdResponse(BaseModel):
    direction: OrderDirection
    ticker: str = Field(pattern=r"^[A-Z]{2,10}$")
    qty: int = Field(ge=1)


class MarketOrderByIdResponse(BaseModel):
    id: UUID
    status: OrderStatus
    user_id: UUID
    body: MarketOrderBodyByIdResponse
