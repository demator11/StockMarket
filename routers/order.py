from fastapi import APIRouter

router_order = APIRouter()


@router_order.get("/api/v1/order/")
def order():
    return {"success": "True"}
