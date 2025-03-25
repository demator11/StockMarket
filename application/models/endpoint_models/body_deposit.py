from pydantic import Field, BaseModel


class CreateDepositRequest(BaseModel):
    ticker: str
    amount: int = Field(gt=0)
