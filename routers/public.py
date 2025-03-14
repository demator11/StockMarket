from fastapi import APIRouter, HTTPException, Response

from models.user import NewUser, User
from models.instrument import Instrument
from models.orderbook import L2OrderBook
from models.transaction import Transaction
from database.repository.user_repository import UserRepository
from database.repository.instrument_repository import InstrumentRepository
from create_token import create_access_token

router_public = APIRouter()


@router_public.post("/api/v1/public/register", summary="Register")
async def register_new_user(new_user: NewUser, response: Response):
    check = await UserRepository.check_has_in_database(new_user.name)
    if check:
        raise HTTPException(
            status_code=409, detail="Пользователь уже существует"
        )
    api_key = create_access_token({"sub": new_user.name})
    result = await UserRepository.create_user(new_user, api_key)
    response.headers["Authorization"] = "TOKEN " + api_key
    return result


@router_public.get("/api/v1/public/instrument", summary="List instruments")
async def get_instrument_list() -> list[Instrument]:
    result = await InstrumentRepository.get_instrument_list()
    return result


@router_public.get(
    "/api/v1/public/orderbook/{ticker}", summary="Get Orderbook"
)
def get_orderbook(ticker: str, qty: int = 10) -> L2OrderBook:
    # достаем список из qty бидов и асков по нужному ticker
    bid_levels = [{"price": 1, "qty": 1}, {"price": 2, "qty": 2}]
    ask_levels = [{"price": 3, "qty": 3}, {"price": 4, "qty": 4}]
    result = L2OrderBook(bid_levels=bid_levels, ask_levels=ask_levels)
    return result


@router_public.get(
    "/api/v1/public/transactions/{ticker}", summary="Get Transaction History"
)
def get_transaction_history(ticker: str, limit: int = 10) -> list[Transaction]:
    # получаем до limit транзакций по нужному ticker
    result = []
    result.append(
        Transaction(
            ticker=ticker,
            amount=1,
            price=2,
            timestamp="2025-03-10T08:51:47.755Z",
        )
    )
    return result
