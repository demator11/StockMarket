from fastapi import APIRouter, HTTPException, Response, Depends

from application.models.endpoints_models.user import (
    NewUserRequest,
    UserResponse,
)
from application.models.orm_models.instrument import Instrument
from application.models.endpoints_models.orderbook import L2OrderBook
from application.models.endpoints_models.transaction import Transaction
from application.database.repository.repositories import (
    get_user_repository,
    get_instrument_repository,
)
from application.database.repository.user_repository import UserRepository
from application.database.repository.instrument_repository import (
    InstrumentRepository,
)
from application.models.orm_models.user import NewUser
from application.token_management import create_access_token

public_router = APIRouter()


@public_router.post("/api/v1/public/register", summary="Register")
async def register_new_user(
    new_user: NewUserRequest,
    response: Response,
    user_repository: UserRepository = Depends(get_user_repository),
):
    new_user = NewUser(name=new_user.name)
    user_exists = await user_repository.exists_in_database(new_user.name)
    if user_exists:
        raise HTTPException(
            status_code=409, detail="Пользователь уже существует"
        )
    api_key = create_access_token({"sub": new_user.name})

    user = await user_repository.create_user(new_user, api_key)
    response.headers["Authorization"] = "TOKEN " + api_key
    return UserResponse(
        id=user.id, name=user.name, role=user.role, api_key=user.api_key
    )


@public_router.get("/api/v1/public/instrument", summary="List instruments")
async def get_instrument_list(
    instrument_repository: InstrumentRepository = Depends(
        get_instrument_repository
    ),
) -> list[Instrument]:
    result = await instrument_repository.get_all()
    return result


@public_router.get(
    "/api/v1/public/orderbook/{ticker}", summary="Get Orderbook"
)
def get_orderbook(ticker: str, qty: int = 10) -> L2OrderBook:
    # достаем список из qty бидов и асков по нужному ticker
    bid_levels = [{"price": 1, "qty": 1}, {"price": 2, "qty": 2}]
    ask_levels = [{"price": 3, "qty": 3}, {"price": 4, "qty": 4}]
    result = L2OrderBook(bid_levels=bid_levels, ask_levels=ask_levels)
    return result


@public_router.get(
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
