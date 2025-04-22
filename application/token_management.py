from uuid import UUID
from datetime import datetime, timedelta, UTC

from dotenv import load_dotenv
from fastapi import Security, HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader
from jose import jwt

from application.database.config import JWT_SECRET_KEY
from application.di.repositories import get_user_repository
from application.database.repository.user_repository import UserRepository
from application.models.database_models.user import UserRole

load_dotenv()

api_key_header = APIKeyHeader(name="Authorization")


async def base_authorization(
    api_key: str,
    user_repository: UserRepository,
    required_role: UserRole | None = None,
) -> UUID:
    user = await user_repository.get_by_api_key(api_key)
    if user is None:
        raise HTTPException(
            status_code=401, detail="Пользователь не авторизован"
        )
    if required_role and user.role != required_role:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    return user.id


async def user_authorization(
    api_key: str = Security(api_key_header),
    user_repository: UserRepository = Depends(get_user_repository),
) -> UUID:
    return await base_authorization(api_key, user_repository)


async def admin_authorization(
    api_key: str = Security(api_key_header),
    user_repository: UserRepository = Depends(get_user_repository),
) -> UUID:
    return await base_authorization(api_key, user_repository, UserRole.admin)


def get_auth_data():
    return {
        "secret_key": JWT_SECRET_KEY,
        "algorithm": "HS256",
    }


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=30)
    to_encode.update({"exp": expire})
    auth_data = get_auth_data()
    encode_jwt = jwt.encode(
        to_encode, auth_data["secret_key"], algorithm=auth_data["algorithm"]
    )
    return encode_jwt
