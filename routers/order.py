from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends

from token_management import user_authorization
from database.repository.order_repository import OrderRepository
from database.repository.repositories import get_order_repository
from models.endpoints_models.order import (
    LimitOrder,
    LimitOrderBody,
    MarketOrderBody,
)
from models.enum_models.order import OrderStatus
from models.endpoints_models.success_response import SuccessResponse

order_router = APIRouter()


@order_router.post("/api/v1/order/", summary="Create Order")
async def create_order_response(
    new_order: LimitOrderBody | MarketOrderBody,
    authorization: UUID = Depends(user_authorization),
    order_repository: OrderRepository = Depends(get_order_repository),
):
    try:
        new_order.price
    except AttributeError:
        return await order_repository.create_market_order(
            new_order, authorization
        )
    return await order_repository.create_limit_order(new_order, authorization)


@order_router.get("/api/v1/order", summary="List Orders")
async def get_orders_list(
    authorization: UUID = Depends(user_authorization),
    order_repository: OrderRepository = Depends(get_order_repository),
):
    result = await order_repository.get_order_list()
    return result


@order_router.get("/api/v1/order/{order_id}", summary="Get Order")
async def get_order_by_id(
    order_id: UUID,
    authorization: UUID = Depends(user_authorization),
    order_repository: OrderRepository = Depends(get_order_repository),
) -> LimitOrder:
    result = await order_repository.get_order_by_id(order_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Ордер не найден")
    return result


@order_router.delete("/api/v1/order/{order_id}", summary="Cancel Order")
async def cancel_order_by_id(
    order_id: UUID,
    authorization: UUID = Depends(user_authorization),
    order_repository: OrderRepository = Depends(get_order_repository),
) -> SuccessResponse:
    result = await order_repository.update_order_status(
        order_id=order_id, status=OrderStatus.cancelled
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Ордер не найден")
    elif not result:
        raise HTTPException(status_code=406, detail="Ордер уже отменён")
    return SuccessResponse()
