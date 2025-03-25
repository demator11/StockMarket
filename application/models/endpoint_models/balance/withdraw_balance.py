from pydantic import Field, BaseModel


class WithdrawBalanceRequest(BaseModel):
    ticker: str
    amount: int = Field(gt=0)
