from enum import StrEnum
from uuid import UUID

from application.models.base import ModelBase


class UserRole(StrEnum):
    user = "USER"
    admin = "ADMIN"


class NewUser(ModelBase):
    name: str


class User(ModelBase):
    id: UUID
    name: str
    role: UserRole = UserRole.user
    api_key: str
