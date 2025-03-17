from uuid import UUID

from pydantic import Field

from models.endpoints_models.base import ModelBase


class Body_deposit_api_v1_balance_deposit_post(ModelBase):
    ticker: str
    amount: int = Field(gt=0)


class BodyDeposit(ModelBase):
    id: UUID
    user_id: UUID
    currency: str
    qty: int = Field(gt=0)
