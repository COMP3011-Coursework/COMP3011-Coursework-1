from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.commodity import Commodity
from app.models.currency import Currency
from app.models.market import Market
from app.models.price import Price
from app.schemas.reference import CommodityResponse, CountryResponse, CurrencyResponse, MarketResponse

router = APIRouter(tags=["reference"])


@router.get(
    "/countries",
    response_model=list[CountryResponse],
    summary="List countries with price data",
    description="Return all countries that have at least one price record, ordered by record count descending.",
    response_description="List of ISO 3166-1 alpha-3 country codes with their price record counts",
)
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


@router.get(
    "/commodities",
    response_model=list[CommodityResponse],
    summary="List all commodities",
    description="Return all food commodities tracked in the system, ordered alphabetically by name.",
    response_description="List of commodities with ID, category, and name",
)
async def list_commodities(
    db: AsyncSession = Depends(get_db),
) -> list[CommodityResponse]:
    result = await db.execute(select(Commodity).order_by(Commodity.name))
    return list(result.scalars().all())


@router.get(
    "/currencies",
    response_model=list[CurrencyResponse],
    summary="List all currencies",
    description="Return all currency codes used in price records, ordered by currency code.",
    response_description="List of currency codes and their full names",
)
async def list_currencies(
    db: AsyncSession = Depends(get_db),
) -> list[CurrencyResponse]:
    result = await db.execute(select(Currency).order_by(Currency.code))
    return list(result.scalars().all())


@router.get(
    "/markets",
    response_model=list[MarketResponse],
    summary="List markets",
    description="Return all markets, optionally filtered by country. Results are ordered alphabetically by market name.",
    response_description="List of markets with location details",
)
async def list_markets(
    db: AsyncSession = Depends(get_db),
    country: Optional[str] = Query(
        default=None,
        min_length=3,
        max_length=3,
        description="Filter by ISO 3166-1 alpha-3 country code, e.g. `ETH`",
    ),
) -> list[MarketResponse]:
    query = select(Market).order_by(Market.name)
    if country is not None:
        query = query.where(Market.countryiso3 == country)
    result = await db.execute(query)
    return list(result.scalars().all())
