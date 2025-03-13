from typing import Annotated
from fastapi import APIRouter, Header, HTTPException

from database.repository.instrument_repository import InstrumentRepository
from models.instrument import Instrument
from models.ok import Ok

router_admin = APIRouter()


@router_admin.post("/api/v1/admin/instrument")
async def add_instrument(
    new_instrument: Instrument,
    authorization: Annotated[str | None, Header()] = None,
) -> Ok:
    # проверяем админ ли юзер, если нет, return Ok(success=False)
    check = await InstrumentRepository.check_has_in_database(
        new_instrument.ticker
    )
    if check:
        raise HTTPException(status_code=409, detail="Тикер уже существует")
    await InstrumentRepository.create_instrument(new_instrument)
    # Данил не бей, в тз именно такой класс указан
    return Ok()


@router_admin.delete("/api/v1/admin/instrument/{ticker}")
def delete_instrument(
    ticker: str, authorization: Annotated[str | None, Header()] = None
) -> Ok:
    # удаляем инструмент
    return Ok()
