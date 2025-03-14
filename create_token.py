import os
from dotenv import load_dotenv

from fastapi import Security
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from jose import jwt
from datetime import datetime, timedelta, timezone

load_dotenv()

token_key = APIKeyHeader(name="Authorization")


class Token(BaseModel):
    token: str


def get_current_token(auth_key: str = Security(token_key)):
    return auth_key


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
