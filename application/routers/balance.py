from uuid import UUID
from fastapi import APIRouter, Depends

from application.token_management import user_authorization
from application.database.repository.balance_repository import (
    BalanceRepository,
)
from application.di.repositories import get_balance_repository

balance_router = APIRouter(prefix="/api/v1/balance")


@balance_router.get("", summary="Get Balance")
async def get_balance(
    authorization: UUID = Depends(user_authorization),
    balance_repository: BalanceRepository = Depends(get_balance_repository),
) -> dict:
    result = await balance_repository.get_balances_by_user_id(authorization)
    return {row.ticker: row.qty for row in result}
