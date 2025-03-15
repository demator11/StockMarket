from uuid import UUID

from typing import Annotated
from fastapi import APIRouter, Header, HTTPException, Depends

from models.user import UserRole
from models.instrument import Instrument
from models.success_response import SuccessResponse
from database.repository.user_repository import UserRepository
from database.repository.instrument_repository import InstrumentRepository
from token_management import admin_authorization, user_authorization


router_admin = APIRouter()


@router_admin.post("/api/v1/admin/instrument")
async def add_instrument(
    new_instrument: Instrument,
    authorization: UUID = Depends(admin_authorization),
) -> SuccessResponse:
    check_ticker = await InstrumentRepository.check_has_in_database(
        new_instrument.ticker
    )
    if check_ticker:
        raise HTTPException(status_code=409, detail="Тикер уже существует")
    await InstrumentRepository.create_instrument(new_instrument)
    return SuccessResponse()


@router_admin.delete("/api/v1/admin/instrument/{ticker}")
def delete_instrument(
    ticker: str, authorization: Annotated[str | None, Header()] = None
) -> SuccessResponse:
    # удаляем инструмент
    return SuccessResponse()


@router_admin.post("/api/v1/admin")
async def get_admin_role(authorization: UUID = Depends(user_authorization)):
    await UserRepository.change_user_role(authorization, UserRole.admin)
    return SuccessResponse()
