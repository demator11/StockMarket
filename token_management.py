import os
from uuid import UUID
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from jose import jwt

from database.repository.user_repository import UserRepository

load_dotenv()

api_key_header = APIKeyHeader(name="Authorization")


async def user_authorization(api_key: str = Security(api_key_header)) -> UUID:
    user_id = await UserRepository.check_user_authorization(api_key)
    if user_id is None:
        raise HTTPException(
            status_code=403, detail="Пользователь не авторизован"
        )
    return user_id


async def admin_authorization(api_key: str = Security(api_key_header)) -> UUID:
    user_id = await UserRepository.check_admin_authorization(api_key)
    if user_id is None:
        raise HTTPException(
            status_code=403, detail="Пользователь не авторизован"
        )
    elif not user_id:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    return user_id


def get_auth_data():
    return {
        "secret_key": os.getenv("SECRET_KEY"),
        "algorithm": os.getenv("ALGORITHM"),
    }


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=30)
    to_encode.update({"exp": expire})
    auth_data = get_auth_data()
    encode_jwt = jwt.encode(
        to_encode, auth_data["secret_key"], algorithm=auth_data["algorithm"]
    )
    return encode_jwt
