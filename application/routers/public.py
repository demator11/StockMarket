from datetime import timedelta, datetime
from typing import Dict, List

from fastapi import APIRouter, HTTPException, Response, Depends

from application.database.repository.order_repository import OrderRepository
from application.database.repository.transaction_repository import (
    TransactionRepository,
)
from application.models.database_models.order import (
    OrderDirection,
)
from application.models.endpoint_models.public.get_candles import (
    CandleStick,
    GetCandlesResponse,
)
from application.models.endpoint_models.public.get_orderbook import (
    GetOrderbookResponse,
    Level,
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
from application.models.database_models.user import User, UserRole
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
    # костыль на время тестов
    if new_user.name == "ADMIN":
        new_user.api_key = "super_admin_api_key_123456789tochkaonelove"
        user = await user_repository.create(new_user, UserRole.admin)
    else:
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
    bid_levels_dict: Dict[int, int] = {}
    ask_levels_dict: Dict[int, int] = {}
    for order in orders:
        assert order.price is not None
        qty = order.qty - order.filled
        if order.direction == OrderDirection.sell:
            if order.price in ask_levels_dict:
                ask_levels_dict[order.price] += qty
            else:
                ask_levels_dict[order.price] = qty
        else:
            if order.price in bid_levels_dict:
                bid_levels_dict[order.price] += qty
            else:
                bid_levels_dict[order.price] = qty

    ask_levels = [
        Level(price=price, qty=qty) for price, qty in ask_levels_dict.items()
    ]
    bid_levels = [
        Level(price=price, qty=qty) for price, qty in bid_levels_dict.items()
    ]

    sorted_ask_levels = sorted(ask_levels, key=lambda x: x.price)
    sorted_bid_levels = sorted(bid_levels, key=lambda x: x.price, reverse=True)
    return GetOrderbookResponse(
        ask_levels=sorted_ask_levels, bid_levels=sorted_bid_levels
    )


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
                amount=transaction.qty,
                price=transaction.price,
                timestamp=transaction.timestamp,
            )
        )
    return result


@public_router.get("/candle/{ticker}", summary="Get Candles")
async def get_candles(
    ticker: str,
    interval_seconds: int,
    from_time: datetime | None = None,
    to_time: datetime | None = None,
    transaction_repository: TransactionRepository = Depends(
        get_transaction_repository
    ),
) -> GetCandlesResponse:
    if interval_seconds < 1:
        raise HTTPException(status_code=422, detail="Недопустимый интервал")
    transaction_list = await transaction_repository.get(ticker)
    transaction_list = [
        t
        for t in transaction_list
        if (from_time is None or t.timestamp >= from_time)
        and (to_time is None or t.timestamp < to_time)
    ]

    if not transaction_list:
        return GetCandlesResponse(ticker=ticker, candles=[])

    delta = timedelta(seconds=interval_seconds)

    candles = []
    current_bucket_start = None
    current_prices: List[int] = []
    current_volume = 0

    for transaction in transaction_list:
        timestamp = transaction.timestamp.timestamp()

        if delta.total_seconds() >= 86400:
            bucket_start = datetime.fromtimestamp(
                timestamp - (timestamp % 86400)
            )
        elif delta.total_seconds() >= 3600:
            bucket_start = datetime.fromtimestamp(
                timestamp - (timestamp % 3600)
            )
        elif delta.total_seconds() >= 60:
            bucket_start = datetime.fromtimestamp(timestamp - (timestamp % 60))
        else:
            bucket_start = datetime.fromtimestamp(
                timestamp - (timestamp % delta.total_seconds())
            )

        if current_bucket_start != bucket_start:
            if current_bucket_start is not None and current_prices:
                candles.append(
                    CandleStick(
                        open_price=current_prices[0],
                        high_price=max(current_prices),
                        low_price=min(current_prices),
                        close_price=current_prices[-1],
                        volume=current_volume,
                        timestamp=current_bucket_start,
                    )
                )

            current_bucket_start = bucket_start
            current_prices = []
            current_volume = 0

        current_prices.append(transaction.price)
        current_volume += transaction.qty

    if current_prices:
        candles.append(
            CandleStick(
                open_price=current_prices[0],
                high_price=max(current_prices),
                low_price=min(current_prices),
                close_price=current_prices[-1],
                volume=current_volume,
                timestamp=current_bucket_start,
            )
        )

    return GetCandlesResponse(ticker=ticker, candles=candles)
