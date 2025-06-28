from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends

from application.config import timestamp_utc
from application.database.repository.app_config_repository import (
    AppConfigRepository,
)
from application.database.repository.balance_repository import (
    BalanceRepository,
)
from application.database.repository.instrument_repository import (
    InstrumentRepository,
)
from application.database.repository.transaction_repository import (
    TransactionRepository,
)
from application.models.database_models.balance import Balance
from application.models.database_models.order import (
    UpdateOrder,
    OrderStatus,
    Order,
    OrderDirection,
)
from application.models.endpoint_models.order.get_order_list import (
    LimitOrderListResponse,
    LimitOrderBodyListResponse,
    MarketOrderListResponse,
    MarketOrderBodyListResponse,
)
from application.order_consumer import process_order
from application.token_management import user_authorization
from application.database.repository.order_repository import OrderRepository
from application.di.repositories import (
    get_order_repository,
    get_app_config_repository,
    get_instrument_repository,
    get_balance_repository,
    get_transaction_repository,
)
from application.models.endpoint_models.order.get_order_by_id import (
    LimitOrderByIdResponse,
    MarketOrderByIdResponse,
    MarketOrderBody,
    LimitOrderBody,
)
from application.models.endpoint_models.order.create_order import (
    CreateOrderRequest,
    CreateOrderResponse,
)
from application.models.endpoint_models.success_response import (
    SuccessResponse,
)
from logger import setup_logging

order_router = APIRouter(prefix="/api/v1/order")
logger = setup_logging(__name__)


@order_router.post("", summary="Create Order")
async def create_order(
    new_order: CreateOrderRequest,
    authorization: UUID = Depends(user_authorization),
    app_config_repository: AppConfigRepository = Depends(
        get_app_config_repository
    ),
    instrument_repository: InstrumentRepository = Depends(
        get_instrument_repository
    ),
    balance_repository: BalanceRepository = Depends(get_balance_repository),
    order_repository: OrderRepository = Depends(get_order_repository),
    transaction_repository: TransactionRepository = Depends(
        get_transaction_repository
    ),
) -> CreateOrderResponse:
    order_body = Order(
        status=OrderStatus.new,
        user_id=authorization,
        timestamp=timestamp_utc(),
        direction=new_order.direction,
        ticker=new_order.ticker,
        qty=new_order.qty,
        price=new_order.price,
    )

    base_asset = await app_config_repository.get("base_asset") or "RUB"
    if order_body.ticker == base_asset:
        raise HTTPException(
            status_code=400,
            detail="Создание заявки на данный эквивалент невозможна",
        )

    ticker_exists = await instrument_repository.exists_in_database(
        order_body.ticker
    )
    if not ticker_exists:
        raise HTTPException(
            status_code=400, detail="Данного тикера не существует"
        )

    result = await process_order(
        current_order=order_body,
        balance_repository=balance_repository,
        order_repository=order_repository,
        transaction_repository=transaction_repository,
        app_config_repository=app_config_repository,
    )

    if result.status_code != 200:
        raise HTTPException(
            status_code=result.status_code, detail=result.detail
        )

    return CreateOrderResponse(order_id=order_body.id)


@order_router.get("", summary="List Orders")
async def get_orders_list(
    authorization: UUID = Depends(user_authorization),
    order_repository: OrderRepository = Depends(get_order_repository),
) -> list[LimitOrderListResponse | MarketOrderListResponse]:
    result = await order_repository.get_all_by_user_id(authorization)
    order_list = []
    for order in result:
        if order.price is None:
            order_list.append(
                MarketOrderListResponse(
                    id=order.id,
                    status=order.status,
                    user_id=order.user_id,
                    timestamp=order.timestamp,
                    body=MarketOrderBodyListResponse(
                        direction=order.direction,
                        ticker=order.ticker,
                        qty=order.qty,
                    ),
                )
            )
        else:
            order_list.append(
                LimitOrderListResponse(
                    id=order.id,
                    status=order.status,
                    user_id=order.user_id,
                    timestamp=order.timestamp,
                    body=LimitOrderBodyListResponse(
                        direction=order.direction,
                        ticker=order.ticker,
                        qty=order.qty,
                        price=order.price,
                    ),
                    filled=order.filled,
                )
            )

    return order_list


@order_router.get("/{order_id}", summary="Get Order")
async def get_order_by_id(
    order_id: UUID,
    authorization: UUID = Depends(user_authorization),
    order_repository: OrderRepository = Depends(get_order_repository),
) -> LimitOrderByIdResponse | MarketOrderByIdResponse:
    order = await order_repository.get_by_id(order_id)
    if order is None:
        raise HTTPException(status_code=400, detail="Ордер не найден")
    if order.price is None:
        return MarketOrderByIdResponse(
            id=order.id,
            status=order.status,
            user_id=order.user_id,
            timestamp=order.timestamp,
            body=MarketOrderBody(
                direction=order.direction,
                ticker=order.ticker,
                qty=order.qty,
            ),
        )
    return LimitOrderByIdResponse(
        id=order.id,
        status=order.status,
        user_id=order.user_id,
        timestamp=order.timestamp,
        body=LimitOrderBody(
            direction=order.direction,
            ticker=order.ticker,
            qty=order.qty,
            price=order.price,
        ),
        filled=order.filled,
    )


@order_router.delete("/{order_id}", summary="Cancel Order")
async def cancel_order_by_id(
    order_id: UUID,
    authorization: UUID = Depends(user_authorization),
    order_repository: OrderRepository = Depends(get_order_repository),
    balance_repository: BalanceRepository = Depends(get_balance_repository),
    app_config_repository: AppConfigRepository = Depends(
        get_app_config_repository
    ),
) -> SuccessResponse:
    order = await order_repository.get_by_id(order_id)
    if order is None:
        logger.info("Order not found")
        raise HTTPException(status_code=400, detail="Ордер не найден")
    elif order.status != OrderStatus.new:
        logger.info(f"Order cannot be cancelled, status: {order.status}")
        raise HTTPException(status_code=409, detail="Ордер нельзя отменить")
    elif order.user_id != authorization:
        logger.info("Another user's request")
        raise HTTPException(
            status_code=400, detail="Вы не можете отменить данный ордер"
        )

    base_asset = await app_config_repository.get("base_asset") or "RUB"
    await order_repository.update(
        UpdateOrder(id=order_id, status=OrderStatus.cancelled)
    )
    assert order.price is not None
    if order.direction == OrderDirection.sell:
        await balance_repository.release(
            Balance(
                user_id=authorization,
                ticker=order.ticker,
                reserve=order.qty - order.filled,
            )
        )
    else:
        await balance_repository.release(
            Balance(
                user_id=authorization,
                ticker=base_asset,
                reserve=order.price * (order.qty - order.filled),
            )
        )

    return SuccessResponse()
