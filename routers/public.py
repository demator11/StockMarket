from fastapi import APIRouter

from models.user import NewUser, User
from models.instrument import Instrument

router_public = APIRouter()


@router_public.post("/api/v1/public/register", summary="Register")
def register_new_user(new_user: NewUser) -> User:
    # добавляем юзера в дб, генерируем id и api_key
    id = "abc"
    api_key = "abc123"
    return User(id=id, name=new_user.name, api_key=api_key)


@router_public.get("/api/v1/public/instrument", summary="List instruments")
def get_instrument_list() -> Instrument:
    # берем какие то там инструменты и отдаем их списком
    instrument = Instrument(name="string", ticker="TICKER")
    return instrument
