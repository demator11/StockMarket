from pydantic import BaseModel, Field


class Body_deposit_api_v1_balance_deposit_post(BaseModel):
    ticker: str
    amount: int = Field(gt=0)
