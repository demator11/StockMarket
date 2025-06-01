from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from application.models.database_models.order import (
    OrderDirection,
    OrderStatus,
)


class LimitOrderBodyListResponse(BaseModel):
    direction: OrderDirection
    ticker: str = Field(pattern=r"^[A-Z]{2,10}$")
    qty: int = Field(ge=1)
    price: int = Field(gt=0)


class LimitOrderListResponse(BaseModel):
    id: UUID
    status: OrderStatus
    user_id: UUID
    timestamp: datetime
    body: LimitOrderBodyListResponse
    filled: int = 0


class MarketOrderBodyListResponse(BaseModel):
    direction: OrderDirection
    ticker: str = Field(pattern=r"^[A-Z]{2,10}$")
    qty: int = Field(ge=1)


class MarketOrderListResponse(BaseModel):
    id: UUID
    status: OrderStatus
    user_id: UUID
    timestamp: datetime
    body: MarketOrderBodyListResponse
