from typing import Annotated
from fastapi import APIRouter, Header
from models.ok import Ok

router_balance = APIRouter()


@router_balance.get("/api/v1/balance/", summary="Get Balance")
def get_balance(api_key: str = Header(default=None)):
    # берем ключ авторизации из заголовка и по нему достаем баланс

    return {"MEMCOIN": 0, "DODGE": 100500}


@router_balance.post("/api/v1/balance/deposit", summary="Deposit")
def do_deposit(api_key: Annotated[str | None, Header()] = None) -> Ok:
    # пытаемся положить на баланс юзера коины
    return Ok()


@router_balance.post("/api/v1/balance/withdraw", summary="Withdraw")
def do_withdraw(api_key: Annotated[str | None, Header()] = None) -> Ok:
    # пытаемся вывести коины с баланса юзера
    return Ok()
