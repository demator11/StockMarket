from uuid import UUID

from pydantic import BaseModel, Field


class WithdrawUserBalanceRequest(BaseModel):
    user_id: UUID
    ticker: str = Field(pattern=r"^[A-Z]{2,10}$")
    amount: int = Field(gt=0)
