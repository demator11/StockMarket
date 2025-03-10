from fastapi import APIRouter

router_balance = APIRouter()


@router_balance.get("/api/v1/balance/")
def balance():
    return {"success": "True"}
