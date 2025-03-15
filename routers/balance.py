from typing import Annotated
from fastapi import APIRouter, Header, Depends, HTTPException

from models.ok import Ok
from models.body_deposit import Body_deposit_api_v1_balance_deposit_post
from models.body_withdraw import Body_deposit_api_v1_balance_withdraw_post
from create_token import Token, get_current_token
from database.repository.balance_repository import BalanceRepository
from database.repository.user_repository import UserRepository

router_balance = APIRouter()


@router_balance.get("/api/v1/balance/", summary="Get Balance")
async def get_balance(authorization: Token = Depends(get_current_token)):
    user_id = await UserRepository.check_user_authorization(authorization)
    if user_id is None:
        raise HTTPException(
            status_code=405, detail="Пользователь не авторизован"
        )
    result = await BalanceRepository.get_user_balance(user_id)
    return result


@router_balance.post("/api/v1/balance/deposit", summary="Deposit")
async def do_deposit(
    deposit: Body_deposit_api_v1_balance_deposit_post,
    authorization: Token = Depends(get_current_token),
) -> Ok:
    user_id = await UserRepository.check_user_authorization(authorization)
    if user_id is None:
        raise HTTPException(
            status_code=405, detail="Пользователь не авторизован"
        )
    await BalanceRepository.create_user_deposit(user_id, deposit)
    return Ok()


@router_balance.post("/api/v1/balance/withdraw", summary="Withdraw")
def do_withdraw(
    body: Body_deposit_api_v1_balance_withdraw_post,
    authorization: Annotated[str | None, Header()] = None,
) -> Ok:
    # пытаемся вывести коины с баланса юзера
    return Ok()
