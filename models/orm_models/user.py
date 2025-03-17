from uuid import UUID

from models.enum_models.user import UserRole
from models.base import ModelBase


class NewUser(ModelBase):
    name: str


class User(ModelBase):
    id: UUID
    name: str
    role: UserRole = UserRole.user
    api_key: str
