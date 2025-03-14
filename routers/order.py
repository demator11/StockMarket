from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, Depends

from create_token import Token, get_current_token
from database.repository.user_repository import UserRepository
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
    authorization: Token = Depends(get_current_token),
):
    user_id = await UserRepository.check_user_authorization(authorization)
    # сюда еще проверку существует ли такой тикер
    if user_id is None:
        raise HTTPException(
            status_code=405, detail="Пользователь не авторизован"
        )
    try:
        new_order.price
    except AttributeError:
        return await OrderRepository.create_market_order(new_order, user_id)
    return await OrderRepository.create_limit_order(new_order, user_id)


@router_order.get("/api/v1/order", summary="List Orders")
async def get_orders_list(
    authorization: Token = Depends(get_current_token),
):
    user_id = await UserRepository.check_user_authorization(authorization)
    if user_id is None:
        raise HTTPException(
            status_code=405, detail="Пользователь не авторизован"
        )
    result = await OrderRepository.get_order_list()
    return result


@router_order.get("/api/v1/order/{order_id}", summary="Get Order")
async def get_order_by_id(
    order_id: UUID, authorization: Token = Depends(get_current_token)
) -> LimitOrder:
    user_id = await UserRepository.check_user_authorization(authorization)
    if user_id is None:
        raise HTTPException(
            status_code=405, detail="Пользователь не авторизован"
        )
    result = await OrderRepository.get_order_by_id(order_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Ордер не найден")
    return result


@router_order.delete("/api/v1/order/{order_id}", summary="Cancel Order")
async def cancel_order_by_id(
    order_id: UUID, authorization: Token = Depends(get_current_token)
) -> Ok:
    user_id = await UserRepository.check_user_authorization(authorization)
    if user_id is None:
        raise HTTPException(
            status_code=405, detail="Пользователь не авторизован"
        )
    result = await OrderRepository.update_order_status(
        order_id=order_id, status=OrderStatus.cancelled
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Ордер не найден")
    elif not result:
        raise HTTPException(status_code=406, detail="Ордер уже отменён")
    return Ok()
