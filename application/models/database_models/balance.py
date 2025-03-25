import uuid
from uuid import UUID

from pydantic import Field

from application.models.base import ModelBase


class Balance(ModelBase):
    id: UUID = Field(default_factory=uuid.uuid4)
    user_id: UUID
    ticker: str
    qty: int = Field(gt=0)
