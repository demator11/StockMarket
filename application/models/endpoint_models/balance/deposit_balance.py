from pydantic import Field, BaseModel


class DepositBalanceRequest(BaseModel):
    ticker: str
    amount: int = Field(gt=0)
