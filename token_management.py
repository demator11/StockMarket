from uuid import UUID
from datetime import datetime, timedelta, UTC

from database.config import JWT_SECRET_KEY, JWT_ALGORITHM
from dotenv import load_dotenv
from fastapi import Security, HTTPException, Depends
from fastapi.security.api_key import APIKeyHeader
from jose import jwt

from database.repository.repositories import get_user_repository
from database.repository.user_repository import UserRepository

load_dotenv()

api_key_header = APIKeyHeader(name="Authorization")


async def user_authorization(
    api_key: str = Security(api_key_header),
    user_repository: UserRepository = Depends(get_user_repository),
) -> UUID:
    user_id = await user_repository.check_user_authorization(api_key)
    if user_id is None:
        raise HTTPException(
            status_code=403, detail="Пользователь не авторизован"
        )
    return user_id


async def admin_authorization(
    api_key: str = Security(api_key_header),
    user_repository: UserRepository = Depends(get_user_repository),
) -> UUID:
    admin_check = await user_repository.check_admin_authorization(api_key)
    if admin_check is None:
        raise HTTPException(
            status_code=403, detail="Пользователь не авторизован"
        )
    elif admin_check is False:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    return admin_check


def get_auth_data():
    return {
        "secret_key": JWT_SECRET_KEY,
        "algorithm": JWT_ALGORITHM,
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
