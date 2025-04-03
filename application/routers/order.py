from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends

from application.database.repository.transaction_repository import (
    TransactionRepository,
)
from application.models.database_models.order import (
    UpdateOrder,
    OrderStatus,
    Order,
    Ticker,
    OrderDirection,
)
from application.models.database_models.transaction import Transaction
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
    get_transaction_repository,
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


@order_router.post("/", summary="Create Order")
async def create_order(
    new_order: CreateOrderRequest,
    authorization: UUID = Depends(user_authorization),
    order_repository: OrderRepository = Depends(get_order_repository),
) -> CreateOrderResponse:
    order_body = Order(
        status=OrderStatus.new,
        user_id=authorization,
        direction=new_order.direction,
        ticker=new_order.ticker,
        qty=new_order.qty,
        price=new_order.price,
    )
    order = await order_repository.create(order_body)
    return CreateOrderResponse(order_id=order.id)


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
) -> SuccessResponse:

    order_check = await order_repository.get_by_id(order_id)
    if order_check is None:
        raise HTTPException(status_code=404, detail="Ордер не найден")
    elif order_check.status == OrderStatus.cancelled:
        raise HTTPException(status_code=406, detail="Ордер уже отменён")

    await order_repository.update(
        UpdateOrder(id=order_id, status=OrderStatus.cancelled)
    )
    return SuccessResponse()


# TODO перенести функцию в репозиторий кролика
@order_router.get("/order/handle", summary="Get Ticker")
async def get_orderbook(
    order_repository: OrderRepository = Depends(get_order_repository),
    transaction_repository: TransactionRepository = Depends(
        get_transaction_repository
    ),
) -> None:
    args = {
        "id": "3f88dadd-e6eb-4e08-9062-42dfbb4ed96b",
        "status": "NEW",
        "user_id": "eb278a3b-38d1-4de7-9e54-cae35a209013",
        "direction": OrderDirection.buy,
        "ticker": "AAA",
        "qty": 140,
        "price": None,
        "filled": 0,
    }
    current_order = Order(**args)
    if current_order.direction == OrderDirection.sell:
        orders = await order_repository.get_by_ticker(
            Ticker(ticker=current_order.ticker, limit=current_order.qty),
            OrderDirection.buy,
        )
    else:
        orders = await order_repository.get_by_ticker(
            Ticker(ticker=current_order.ticker, limit=current_order.qty),
            OrderDirection.sell,
        )
    changed_orders_list = []
    transactions_list = []
    ticker_count = 0
    for order in orders:
        if ticker_count == current_order.qty:
            break
        amount_need_ticker = current_order.qty - ticker_count
        amount_available_ticker = order.qty - order.filled
        if current_order.price is None:
            if amount_need_ticker >= amount_available_ticker:
                ticker_filled = amount_available_ticker
                order.filled = order.qty
                changed_orders_list.append(order)
                ticker_count += ticker_filled
            else:
                ticker_filled = amount_need_ticker
                order.filled += ticker_filled
                changed_orders_list.append(order)
                ticker_count += ticker_filled

        else:
            if order.price == current_order.price:
                ticker_filled = min(
                    amount_need_ticker, amount_available_ticker
                )
                order.filled += ticker_filled
                current_order.filled += ticker_filled
                changed_orders_list.append(order)
                ticker_count += ticker_filled
            else:
                break
        transactions_list.append(
            Transaction(
                ticker=current_order.ticker,
                qty=ticker_filled,
                price=order.price,
            )
        )
    current_order.filled = ticker_count
    changed_orders_list.append(current_order)
