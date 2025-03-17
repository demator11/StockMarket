from pydantic import Field

from models.base import ModelBase


class Body_deposit_api_v1_balance_withdraw_post(ModelBase):
    ticker: str
    amount: int = Field(gt=0)
