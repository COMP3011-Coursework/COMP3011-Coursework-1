from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.commodity import Commodity
from app.models.currency import Currency
from app.models.market import Market
from app.models.price import Price
from app.schemas.reference import CommodityResponse, CountryResponse, CurrencyResponse, MarketResponse

router = APIRouter(tags=["reference"])


@router.get("/countries", response_model=list[CountryResponse])
async def list_countries(
    db: AsyncSession = Depends(get_db),
) -> list[CountryResponse]:
    query = (
        select(Price.countryiso3, func.count().label("count"))
        .group_by(Price.countryiso3)
        .order_by(func.count().desc())
    )
    result = await db.execute(query)
    rows = result.all()
    return [CountryResponse(countryiso3=row.countryiso3, count=row.count) for row in rows]


@router.get("/commodities", response_model=list[CommodityResponse])
async def list_commodities(
    db: AsyncSession = Depends(get_db),
) -> list[CommodityResponse]:
    result = await db.execute(select(Commodity).order_by(Commodity.name))
    return list(result.scalars().all())


@router.get("/currencies", response_model=list[CurrencyResponse])
async def list_currencies(
    db: AsyncSession = Depends(get_db),
) -> list[CurrencyResponse]:
    result = await db.execute(select(Currency).order_by(Currency.code))
    return list(result.scalars().all())


@router.get("/markets", response_model=list[MarketResponse])
async def list_markets(
    db: AsyncSession = Depends(get_db),
    country: Optional[str] = None,
) -> list[MarketResponse]:
    query = select(Market)
    if country is not None:
        query = query.where(Market.countryiso3 == country)
    result = await db.execute(query)
    return list(result.scalars().all())
