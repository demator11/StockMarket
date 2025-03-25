import uuid
from enum import StrEnum
from uuid import UUID

from pydantic import Field

from application.models.base import ModelBase


class UserRole(StrEnum):
    user = "USER"
    admin = "ADMIN"


class User(ModelBase):
    id: UUID = Field(default_factory=uuid.uuid4)
    name: str
    role: UserRole = UserRole.user
    api_key: str
