import uuid
from uuid import UUID

from pydantic import Field

from application.models.base import ModelBase


class OutboxMessage(ModelBase):
    id: UUID = Field(default_factory=uuid.uuid4)
    payload: str
    is_sent: bool = False
