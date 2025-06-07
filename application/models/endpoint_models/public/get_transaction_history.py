from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class GetTransactionHistoryResponse(BaseModel):
    id: UUID
    ticker: str
    amount: int
    price: int
    timestamp: datetime
