from uuid import UUID

from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from application.models.orm_models.user import UserOrm
from application.models.database_models.user import User, UserRole


class UserRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(self, user: User, role: UserRole = UserRole.user) -> User:
        result = await self.db_session.scalars(
            insert(UserOrm)
            .values(name=user.name, role=role, api_key=user.api_key)
            .returning(UserOrm)
        )
        return User.model_validate(result.one())

    async def exists_in_database(self, user_name: str) -> bool:
        result = await self.db_session.scalars(
            select(UserOrm.name).where(UserOrm.name == user_name)
        )
        return result.one_or_none() is not None

    async def exists_id_in_database(self, user_id: UUID):
        result = await self.db_session.scalars(
            select(UserOrm.id).where(UserOrm.id == user_id)
        )
        return result.one_or_none()

    async def get_by_api_key(self, api_key: str) -> UserOrm | None:
        result = await self.db_session.scalars(
            select(UserOrm).where(UserOrm.api_key == api_key)
        )
        return result.one_or_none()

    async def change_user_role(self, user_id: UUID, role: UserRole) -> None:
        await self.db_session.execute(
            update(UserOrm).where(UserOrm.id == user_id).values(role=role)
        )

    async def delete(self, user_id: UUID) -> User | None:
        result = await self.db_session.scalars(
            delete(UserOrm).where(UserOrm.id == user_id).returning(UserOrm)
        )
        result = result.one_or_none()
        if result is None:
            return None
        return User.model_validate(result)
