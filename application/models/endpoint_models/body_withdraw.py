from pydantic import Field, BaseModel


class CreateWithdrawRequest(BaseModel):
    ticker: str
    amount: int = Field(gt=0)
