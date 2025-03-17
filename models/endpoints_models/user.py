from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from models.enum_models.user import UserRole


class NewUser(BaseModel):
    name: str = Field(min_length=3)


class User(BaseModel):
    id: UUID
    name: str
    role: UserRole = UserRole.user
    api_key: str

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
