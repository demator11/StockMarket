from uuid import UUID
from fastapi import APIRouter, Depends

from application.models.database_models.balance import Balance
from application.models.endpoint_models.success_response import (
    SuccessResponse,
)
from application.models.endpoint_models.balance.deposit_balance import (
    DepositUserBalanceRequest,
)
from application.models.endpoint_models.balance.withdraw_balance import (
    WithdrawBalanceRequest,
)
from application.models.database_models.deposit import Deposit
from application.token_management import user_authorization
from application.database.repository.balance_repository import (
    BalanceRepository,
)
from application.di.repositories import get_balance_repository

balance_router = APIRouter(prefix="/api/v1/balance")


@balance_router.get("/", summary="Get Balance")
async def get_balance(
    authorization: UUID = Depends(user_authorization),
    balance_repository: BalanceRepository = Depends(get_balance_repository),
) -> dict:
    result = await balance_repository.get_user_by_id(authorization)
    return {row.ticker: row.qty for row in result}
