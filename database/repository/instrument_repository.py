from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.orm_models.instrument import Instrument
from models.database_models.instrument import InstrumentOrm


class InstrumentRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_instrument(
        self, new_instrument: Instrument
    ) -> Instrument:
        result = await self.db_session.scalars(
            insert(InstrumentOrm)
            .values(
                name=new_instrument.name,
                ticker=new_instrument.ticker,
            )
            .returning(InstrumentOrm)
        )
        return Instrument.from_orm(result.one())

    async def check_instrument_in_database(self, ticker: str) -> bool:
        query = select(InstrumentOrm.ticker).where(
            InstrumentOrm.ticker == ticker
        )
        result = await self.db_session.scalars(query)
        return result.one_or_none() is not None

    async def get_all_instrument_list(self) -> list[Instrument]:
        query = select(InstrumentOrm)
        result = await self.db_session.execute(query)
        return [Instrument.from_orm(x) for x in result.scalars().all()]
