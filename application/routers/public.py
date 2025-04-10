from fastapi import APIRouter, HTTPException, Response, Depends

from application.database.repository.order_repository import OrderRepository
from application.database.repository.transaction_repository import (
    TransactionRepository,
)
from application.models.database_models.order import (
    OrderStatus,
    OrderDirection,
)
from application.models.endpoint_models.public.get_orderbook import (
    GetOrderbookResponse,
    LevelResponse,
)
from application.models.endpoint_models.public.get_transaction_history import (
    GetTransactionHistoryResponse,
)
from application.models.endpoint_models.public.list_instrument import (
    InstrumentListResponse,
)
from application.models.endpoint_models.public.create_user import (
    CreateUserRequest,
    CreateUserResponse,
)
from application.di.repositories import (
    get_user_repository,
    get_instrument_repository,
    get_order_repository,
    get_transaction_repository,
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
async def list_instrument(
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
async def get_orderbook(
    ticker: str,
    limit: int = 10,
    order_repository: OrderRepository = Depends(get_order_repository),
) -> GetOrderbookResponse:
    if limit <= 0:
        limit = 10
    orders = await order_repository.get_by_ticker(ticker, limit)
    bid_levels, ask_levels = [], []
    for order in orders:
        if (
            order.status == OrderStatus.cancelled
            or order.status == OrderStatus.executed
        ):
            continue
        if order.direction == OrderDirection.sell:
            ask_levels.append(LevelResponse(price=order.price, qty=order.qty))
        else:
            bid_levels.append(LevelResponse(price=order.price, qty=order.qty))

    return GetOrderbookResponse(ask_levels=ask_levels, bid_levels=bid_levels)


@public_router.get("/transactions/{ticker}", summary="Get Transaction History")
async def get_transaction_history(
    ticker: str,
    limit: int = 10,
    transaction_repository: TransactionRepository = Depends(
        get_transaction_repository
    ),
) -> list[GetTransactionHistoryResponse]:
    transactions = await transaction_repository.get(ticker, limit)
    result = []
    for transaction in transactions:
        result.append(
            GetTransactionHistoryResponse(
                id=transaction.id,
                ticker=transaction.ticker,
                qty=transaction.qty,
                price=transaction.price,
                timestamp=transaction.timestamp,
            )
        )
    return result
