from fastapi import APIRouter, Header

router_balance = APIRouter()


@router_balance.get("/api/v1/balance/", summary="Get Balance")
def get_balance(api_key: str = Header(default=None)):
    # берем ключ авторизации из заголовка и по нему достаем баланс

    return {"MEMCOIN": 0, "DODGE": 100500}
