from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class GetTransactionHistoryResponse(BaseModel):
    id: UUID
    ticker: str
    qty: int
    price: int
    timestamp: datetime
