from fastapi import APIRouter, HTTPException, Response, Depends

from application.models.endpoint_models.intrument.get_list_instrument import (
    InstrumentListResponse,
)
from application.models.endpoint_models.public.create_user import (
    CreateUserRequest,
    CreateUserResponse,
)
from application.models.endpoint_models.order.orderbook import L2OrderBook
from application.models.endpoint_models.public.get_transaction_history import (
    Transaction,
)
from application.di.repositories import (
    get_user_repository,
    get_instrument_repository,
)
from application.database.repository.user_repository import UserRepository
from application.database.repository.instrument_repository import (
    InstrumentRepository,
)
from application.models.database_models.user import User
from application.token_management import create_access_token

public_router = APIRouter(prefix="/api/v1/public")


@public_router.post("/register", summary="Register")
async def register_new_user(
    new_user: CreateUserRequest,
    response: Response,
    user_repository: UserRepository = Depends(get_user_repository),
) -> CreateUserResponse:
    user_exists = await user_repository.exists_in_database(new_user.name)
    if user_exists:
        raise HTTPException(
            status_code=409, detail="Пользователь уже существует"
        )

    api_key = create_access_token({"sub": new_user.name})
    new_user = User(name=new_user.name, api_key=api_key)
    user = await user_repository.create(new_user)
    response.headers["Authorization"] = "TOKEN " + api_key

    return CreateUserResponse(
        id=user.id, name=user.name, role=user.role, api_key=user.api_key
    )


@public_router.get("/instrument", summary="List instruments")
async def get_list_instrument(
    instrument_repository: InstrumentRepository = Depends(
        get_instrument_repository
    ),
) -> list[InstrumentListResponse]:
    result = await instrument_repository.get_all()
    instrument_list = []
    for instrument in result:
        instrument_list.append(
            InstrumentListResponse(
                name=instrument.name, ticker=instrument.ticker
            )
        )
    return instrument_list


@public_router.get("/orderbook/{ticker}", summary="Get Orderbook")
def get_orderbook(ticker: str, qty: int = 10) -> L2OrderBook:
    # достаем список из qty бидов и асков по нужному ticker
    bid_levels = [{"price": 1, "qty": 1}, {"price": 2, "qty": 2}]
    ask_levels = [{"price": 3, "qty": 3}, {"price": 4, "qty": 4}]
    result = L2OrderBook(bid_levels=bid_levels, ask_levels=ask_levels)
    return result


@public_router.get("/transactions/{ticker}", summary="Get Transaction History")
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
