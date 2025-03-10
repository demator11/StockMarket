from fastapi import APIRouter

from models.user import NewUser, User
from models.instrument import Instrument
from models.orderbook import L2OrderBook

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


@router_public.get(
    "/api/v1/public/orderbook/{ticker}", summary="Get Orderbook"
)
def get_orderbook(ticker: str, qty: int = 10) -> L2OrderBook:
    # достаем список из qty бидов и асков по нужному ticker
    bid_levels = [{"price": 1, "qty": 1}, {"price": 2, "qty": 2}]
    ask_levels = [{"price": 3, "qty": 3}, {"price": 4, "qty": 4}]
    result = L2OrderBook(bid_levels=bid_levels, ask_levels=ask_levels)
    return result
