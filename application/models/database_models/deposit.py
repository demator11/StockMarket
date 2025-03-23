from uuid import UUID

from pydantic import Field

from application.models.base import ModelBase


class NewDeposit(ModelBase):
    user_id: UUID
    ticker: str
    qty: int = Field(gt=0)


class Deposit(ModelBase):
    id: UUID
    user_id: UUID
    ticker: str
    qty: int = Field(gt=0)
