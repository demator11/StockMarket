from uuid import UUID

from pydantic import Field

from models.base import ModelBase


class Deposit(ModelBase):
    id: UUID
    user_id: UUID
    currency: str
    qty: int = Field(gt=0)
