import asyncio
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
from application.database.repository.outbox_message_repository import (
    OutboxMessageRepository,
)
from application.models.database_models.balance import Balance
from application.models.database_models.order import (
    UpdateOrder,
    OrderStatus,
    Order,
    OrderDirection,
)
from application.models.database_models.outbox_message import OutboxMessage
from application.models.endpoint_models.order.get_order_list import (
    LimitOrderListResponse,
    LimitOrderBodyListResponse,
    MarketOrderListResponse,
    MarketOrderBodyListResponse,
)
from application.token_management import user_authorization
from application.database.repository.order_repository import OrderRepository
from application.di.repositories import (
    get_order_repository,
    get_outbox_message_repository,
    get_app_config_repository,
    get_instrument_repository,
    get_balance_repository,
)
from application.models.endpoint_models.order.get_order_by_id import (
    LimitOrderByIdResponse,
    MarketOrderByIdResponse,
    MarketOrderBodyByIdResponse,
    LimitOrderBodyByIdResponse,
)
from application.models.endpoint_models.order.create_order import (
    CreateOrderRequest,
    CreateOrderResponse,
)
from application.models.endpoint_models.success_response import (
    SuccessResponse,
)

order_router = APIRouter(prefix="/api/v1/order")


@order_router.post("", summary="Create Order")
async def create_order(
    new_order: CreateOrderRequest,
    authorization: UUID = Depends(user_authorization),
    outbox_message_repository: OutboxMessageRepository = Depends(
        get_outbox_message_repository
    ),
    app_config_repository: AppConfigRepository = Depends(
        get_app_config_repository
    ),
    instrument_repository: InstrumentRepository = Depends(
        get_instrument_repository
    ),
    balance_repository: BalanceRepository = Depends(get_balance_repository),
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

    user_base_asset_balance = (
        await balance_repository.get_balance_by_user_id_and_ticker(
            authorization, base_asset
        )
    )
    user_current_ticker_balance = (
        await balance_repository.get_balance_by_user_id_and_ticker(
            authorization, order_body.ticker
        )
    )
    if order_body.direction == OrderDirection.sell:
        if user_current_ticker_balance is None:
            raise HTTPException(
                status_code=400,
                detail=f"{order_body.ticker} отсутствует на балансе",
            )
        elif user_current_ticker_balance.qty < order_body.qty:
            raise HTTPException(
                status_code=400,
                detail=f"Недостаточно {user_current_ticker_balance.ticker} на балансе",  # noqa
            )
        await balance_repository.reserve(
            Balance(
                user_id=order_body.user_id,
                ticker=order_body.ticker,
                reserve=order_body.qty,
            )
        )
    else:
        if user_base_asset_balance is None:
            raise HTTPException(
                status_code=400, detail=f"{base_asset} отсутствует на балансе"
            )
        elif order_body.price is not None:
            if user_base_asset_balance.qty < order_body.price * order_body.qty:
                raise HTTPException(
                    status_code=400,
                    detail=f"Недостаточно {user_base_asset_balance.ticker} на балансе",  # noqa
                )
            await balance_repository.reserve(
                Balance(
                    user_id=order_body.user_id,
                    ticker=user_base_asset_balance.ticker,
                    reserve=order_body.price * order_body.qty,
                )
            )
    await outbox_message_repository.create(
        OutboxMessage(
            id=order_body.id, payload=str(order_body.model_dump_json())
        )
    )
    # костыль
    await asyncio.sleep(0.5)
    return CreateOrderResponse(order_id=order_body.id)


@order_router.get("", summary="List Orders")
async def get_orders_list(
    authorization: UUID = Depends(user_authorization),
    order_repository: OrderRepository = Depends(get_order_repository),
) -> list[LimitOrderListResponse | MarketOrderListResponse]:
    result = await order_repository.get_all()
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
        raise HTTPException(status_code=404, detail="Ордер не найден")
    if order.price is None:
        return MarketOrderByIdResponse(
            id=order.id,
            status=order.status,
            user_id=order.user_id,
            timestamp=order.timestamp,
            body=MarketOrderBodyByIdResponse(
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
        body=LimitOrderBodyByIdResponse(
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
) -> SuccessResponse:
    order = await order_repository.get_by_id(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Ордер не найден")
    elif order.status == OrderStatus.cancelled:
        raise HTTPException(status_code=406, detail="Ордер уже отменён")

    await order_repository.update(
        UpdateOrder(id=order_id, status=OrderStatus.cancelled)
    )
    assert order.price is not None
    await balance_repository.release(
        Balance(
            user_id=authorization,
            ticker=order.ticker,
            reserve=order.price * (order.qty - order.filled),
        )
    )

    return SuccessResponse()
