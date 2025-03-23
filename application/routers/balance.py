from uuid import UUID
from fastapi import APIRouter, Depends

from application.models.endpoints_models.success_response import (
    SuccessResponse,
)
from application.models.endpoints_models.body_deposit import (
    Body_deposit_api_v1_balance_deposit_post,
)
from application.models.endpoints_models.body_withdraw import (
    Body_deposit_api_v1_balance_withdraw_post,
)
from application.models.orm_models.deposit import NewDeposit
from application.token_management import user_authorization
from application.database.repository.balance_repository import (
    BalanceRepository,
)
from application.database.repository.repositories import get_balance_repository

balance_router = APIRouter()


@balance_router.get("/api/v1/balance/", summary="Get Balance")
async def get_balance(
    authorization: UUID = Depends(user_authorization),
    balance_repository: BalanceRepository = Depends(get_balance_repository),
):
    result = await balance_repository.get_user_by_id(authorization)
    balance_dict = {}
    if result is None:
        return balance_dict
    for row in result:
        balance_dict[row.ticker] = row.qty
    return balance_dict


@balance_router.post("/api/v1/balance/deposit", summary="Deposit")
async def do_deposit(
    deposit: Body_deposit_api_v1_balance_deposit_post,
    authorization: UUID = Depends(user_authorization),
    balance_repository: BalanceRepository = Depends(get_balance_repository),
) -> SuccessResponse:
    deposit = NewDeposit(
        user_id=authorization, ticker=deposit.ticker, qty=deposit.amount
    )
    await balance_repository.create_user_deposit(deposit)
    return SuccessResponse()


@balance_router.post("/api/v1/balance/withdraw", summary="Withdraw")
def do_withdraw(
    body: Body_deposit_api_v1_balance_withdraw_post,
    authorization: UUID = Depends(user_authorization),
) -> SuccessResponse:
    # пытаемся вывести коины с баланса юзера
    return SuccessResponse()
