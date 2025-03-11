from typing import Annotated
from fastapi import APIRouter, Header
from uuid import UUID
from models.order import LimitOrderBody, LimitOrder, CreateOrderResponse
from models.ok import Ok

router_order = APIRouter()


@router_order.post("/api/v1/order/", summary="Create Order")
def create_order_response(
    new_order: LimitOrderBody,
    authorization: Annotated[str | None, Header()] = None,
) -> CreateOrderResponse:
    # создаем order и присваиваем id
    order_id = 123
    return CreateOrderResponse(order_id=order_id)


@router_order.get("/api/v1/order", summary="List Orders")
def get_orders_list(
    authorization: Annotated[str | None, Header()] = None,
) -> list[LimitOrder]:
    # получаем список order
    res = []
    return res


@router_order.get("/api/v1/order/{order_id}", summary="Get Order")
def get_order_by_id(
    order_id: UUID, authorization: Annotated[str | None, Header()] = None
) -> LimitOrder:
    # получаем нужный order
    return LimitOrder()


@router_order.delete("/api/v1/order/{order_id}", summary="Cancel Order")
def cancel_order_by_id(
    order_id: UUID, authorization: Annotated[str | None, Header()] = None
) -> Ok:
    # отменяем ордер
    return Ok()
