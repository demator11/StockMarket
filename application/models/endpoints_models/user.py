from uuid import UUID

from pydantic import Field

from application.models.enum_models.user import UserRole
from application.models.base import ModelBase


class NewUserRequest(ModelBase):
    name: str = Field(min_length=3)


class UserResponse(ModelBase):
    id: UUID
    name: str
    role: UserRole = UserRole.user
    api_key: str
