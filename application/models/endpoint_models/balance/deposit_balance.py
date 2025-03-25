from pydantic import Field, BaseModel


class DepositBalanceRequest(BaseModel):
    ticker: str = Field(pattern=r"^[A-Z]{2,10}$")
    amount: int = Field(gt=0)
