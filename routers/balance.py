from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Header, Depends, HTTPException

from models.ok import Ok
from models.body_deposit import Body_deposit_api_v1_balance_deposit_post
from models.body_withdraw import Body_deposit_api_v1_balance_withdraw_post
from token_management import get_current_token
from database.repository.balance_repository import BalanceRepository
from database.repository.user_repository import UserRepository

router_balance = APIRouter()


@router_balance.get("/api/v1/balance/", summary="Get Balance")
async def get_balance(authorization: UUID = Depends(get_current_token)):
    result = await BalanceRepository.get_user_balance(authorization)
    return result


@router_balance.post("/api/v1/balance/deposit", summary="Deposit")
async def do_deposit(
    deposit: Body_deposit_api_v1_balance_deposit_post,
    authorization: UUID = Depends(get_current_token),
) -> Ok:
    await BalanceRepository.create_user_deposit(authorization, deposit)
    return Ok()


@router_balance.post("/api/v1/balance/withdraw", summary="Withdraw")
def do_withdraw(
    body: Body_deposit_api_v1_balance_withdraw_post,
    authorization: UUID = Depends(get_current_token),
) -> Ok:
    # пытаемся вывести коины с баланса юзера
    return Ok()
