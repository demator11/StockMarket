from pydantic import Field

from application.models.base import ModelBase


class Body_deposit_api_v1_balance_deposit_post(ModelBase):
    ticker: str
    amount: int = Field(gt=0)
