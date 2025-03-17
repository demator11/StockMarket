from uuid import UUID
from fastapi import APIRouter, Depends

from models.endpoints_models.success_response import SuccessResponse
from models.endpoints_models.body_deposit import (
    Body_deposit_api_v1_balance_deposit_post,
)
from models.endpoints_models.body_withdraw import (
    Body_deposit_api_v1_balance_withdraw_post,
)
from token_management import user_authorization
from database.repository.balance_repository import BalanceRepository
from database.repository.repositories import get_balance_repository

balance_router = APIRouter()


@balance_router.get("/api/v1/balance/", summary="Get Balance")
async def get_balance(
    authorization: UUID = Depends(user_authorization),
    balance_repository: BalanceRepository = Depends(get_balance_repository),
):
    result = await balance_repository.get_user_balance(authorization)
    return result


@balance_router.post("/api/v1/balance/deposit", summary="Deposit")
async def do_deposit(
    deposit: Body_deposit_api_v1_balance_deposit_post,
    authorization: UUID = Depends(user_authorization),
    balance_repository: BalanceRepository = Depends(get_balance_repository),
) -> SuccessResponse:
    await balance_repository.create_user_deposit(authorization, deposit)
    return SuccessResponse()


@balance_router.post("/api/v1/balance/withdraw", summary="Withdraw")
def do_withdraw(
    body: Body_deposit_api_v1_balance_withdraw_post,
    authorization: UUID = Depends(user_authorization),
) -> SuccessResponse:
    # пытаемся вывести коины с баланса юзера
    return SuccessResponse()
