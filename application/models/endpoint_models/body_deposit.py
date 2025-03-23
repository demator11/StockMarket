from pydantic import Field, BaseModel


class CreateBodyDepositRequest(BaseModel):
    ticker: str
    amount: int = Field(gt=0)
