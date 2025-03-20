from uuid import UUID

from typing import Annotated
from fastapi import APIRouter, Header, HTTPException, Depends

from models.enum_models.user import UserRole
from models.endpoints_models.instrument import InstrumentRequest
from models.endpoints_models.success_response import SuccessResponse
from database.repository.user_repository import UserRepository
from database.repository.instrument_repository import InstrumentRepository
from database.repository.repositories import (
    get_instrument_repository,
    get_user_repository,
)
from models.orm_models.instrument import Instrument
from token_management import admin_authorization, user_authorization


admin_router = APIRouter()


@admin_router.post("/api/v1/admin/instrument")
async def add_instrument(
    new_instrument: InstrumentRequest,
    authorization: UUID = Depends(admin_authorization),
    instrument_repository: InstrumentRepository = Depends(
        get_instrument_repository
    ),
) -> SuccessResponse:
    new_instrument = Instrument(
        name=new_instrument.name, ticker=new_instrument.ticker
    )
    check_ticker = await instrument_repository.exists_in_database(
        new_instrument.ticker
    )
    if check_ticker is not False:
        raise HTTPException(status_code=400, detail="Тикер уже существует")
    await instrument_repository.create(new_instrument)
    return SuccessResponse()


@admin_router.delete("/api/v1/admin/instrument/{ticker}")
def delete_instrument(
    ticker: str,
    authorization: Annotated[str | None, Header()] = None,
    instrument_repository: InstrumentRepository = Depends(
        get_instrument_repository
    ),
) -> SuccessResponse:
    # удаляем инструмент
    return SuccessResponse()


@admin_router.post("/api/v1/admin")
async def get_admin_role(
    authorization: UUID = Depends(user_authorization),
    user_repository: UserRepository = Depends(get_user_repository),
):
    await user_repository.change_user_role(authorization, UserRole.admin)
    return SuccessResponse()
