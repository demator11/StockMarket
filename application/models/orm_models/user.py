from uuid import UUID

from application.models.enum_models.user import UserRole
from application.models.base import ModelBase


class NewUser(ModelBase):
    name: str


class User(ModelBase):
    id: UUID
    name: str
    role: UserRole = UserRole.user
    api_key: str
