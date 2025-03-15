from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends

from token_management import get_current_token
from database.repository.order_repository import OrderRepository
from models.order import (
    LimitOrder,
    LimitOrderBody,
    MarketOrderBody,
    OrderStatus,
)
from models.ok import Ok

router_order = APIRouter()


@router_order.post("/api/v1/order/", summary="Create Order")
async def create_order_response(
    new_order: LimitOrderBody | MarketOrderBody,
    authorization: UUID = Depends(get_current_token),
):
    try:
        new_order.price
    except AttributeError:
        return await OrderRepository.create_market_order(
            new_order, authorization
        )
    return await OrderRepository.create_limit_order(new_order, authorization)


@router_order.get("/api/v1/order", summary="List Orders")
async def get_orders_list(
    authorization: UUID = Depends(get_current_token),
):
    result = await OrderRepository.get_order_list()
    return result


@router_order.get("/api/v1/order/{order_id}", summary="Get Order")
async def get_order_by_id(
    order_id: UUID, authorization: UUID = Depends(get_current_token)
) -> LimitOrder:
    result = await OrderRepository.get_order_by_id(order_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Ордер не найден")
    return result


@router_order.delete("/api/v1/order/{order_id}", summary="Cancel Order")
async def cancel_order_by_id(
    order_id: UUID, authorization: UUID = Depends(get_current_token)
) -> Ok:
    result = await OrderRepository.update_order_status(
        order_id=order_id, status=OrderStatus.cancelled
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Ордер не найден")
    elif not result:
        raise HTTPException(status_code=406, detail="Ордер уже отменён")
    return Ok()
