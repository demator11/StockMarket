from pydantic import Field, BaseModel


class CreateBodyWithdrawRequest(BaseModel):
    ticker: str
    amount: int = Field(gt=0)
