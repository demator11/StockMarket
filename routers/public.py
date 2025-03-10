from fastapi import APIRouter

from models.user import NewUser, User

router_public = APIRouter()


@router_public.post("/api/v1/public/register", summary="Register")
def register_new_user(new_user: NewUser) -> User:
    # добавляем юзера в дб, генерируем id и api_key
    id = "abc"
    api_key = "abc123"
    return User(id=id, name=new_user.name, api_key=api_key)
