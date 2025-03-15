from uuid import UUID

from sqlalchemy import select, insert, update

from database.engine import async_session_factory
from database.database_models.user import UserOrm
from models.user import User, NewUser, UserRole


class UserRepository:
    @staticmethod
    async def create_user(new_user: NewUser, api_key: str) -> User:
        async with async_session_factory.begin() as session:
            result = await session.scalars(
                insert(UserOrm)
                .values(
                    name=new_user.name, role=UserRole.user, api_key=api_key
                )
                .returning(UserOrm)
            )
            return User.from_orm(result.one())

    @staticmethod
    async def check_has_in_database(user_name: str) -> bool:
        async with async_session_factory() as session:
            query = select(UserOrm.name).filter(UserOrm.name == user_name)
            result = await session.execute(query)
            if result.first() is None:
                return False
            return True

    @staticmethod
    async def check_user_authorization(api_key: str):
        async with async_session_factory() as session:
            query = select(UserOrm.id).filter(UserOrm.api_key == api_key)
            result = await session.execute(query)
            result = result.first()
            if result is None:
                return None
            return result[0]

    @staticmethod
    async def check_admin_authorization(api_key: str):
        async with async_session_factory() as session:
            query = select(UserOrm.id, UserOrm.role).filter(
                UserOrm.api_key == api_key
            )
            result = await session.execute(query)
            result = result.first()
            if result is None:
                return None
            elif result[1] == "ADMIN":
                return result[0]
            return False

    @staticmethod
    async def change_user_role(user_id: UUID, role: UserRole):
        async with async_session_factory.begin() as session:
            await session.execute(
                update(UserOrm).where(UserOrm.id == user_id).values(role=role)
            )
