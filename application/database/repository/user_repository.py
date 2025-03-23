from uuid import UUID

from sqlalchemy import select, insert, update
from sqlalchemy.ext.asyncio import AsyncSession

from application.models.orm_models.user import UserOrm
from application.models.database_models.user import User, NewUser
from application.models.enum_models.user import UserRole


class UserRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(self, new_user: NewUser, api_key: str) -> User:
        result = await self.db_session.scalars(
            insert(UserOrm)
            .values(name=new_user.name, role=UserRole.user, api_key=api_key)
            .returning(UserOrm)
        )
        return User.model_validate(result.one())

    async def exists_in_database(self, user_name: str) -> bool:
        query = select(UserOrm.name).where(UserOrm.name == user_name)
        result = await self.db_session.scalars(query)
        return result.one_or_none() is not None

    async def get_by_api_key(self, api_key: str) -> User | None:
        query = select(UserOrm).where(UserOrm.api_key == api_key)
        result = await self.db_session.scalars(query)
        return result.one_or_none()

    async def change_user_role(self, user_id: UUID, role: UserRole) -> None:
        await self.db_session.execute(
            update(UserOrm).where(UserOrm.id == user_id).values(role=role)
        )
