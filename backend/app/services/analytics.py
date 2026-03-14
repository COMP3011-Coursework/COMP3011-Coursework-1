from datetime import date

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.commodity import Commodity
from app.models.market import Market
from app.models.price import Price
from app.schemas.analytics import (
    MarketLatestPrice,
    MarketSummaryResponse,
    RegionalComparisonResponse,
    RegionalItem,
    TrendPoint,
    TrendResponse,
    VolatilityItem,
    VolatilityResponse,
)


async def get_price_trends(
    db: AsyncSession,
    country: str,
    commodity_id: int,
    date_from: date | None,
    date_to: date | None,
) -> TrendResponse:
    filters = [
        Price.countryiso3 == country,
        Price.commodity_id == commodity_id,
        Price.usdprice.is_not(None),
    ]
    if date_from:
        filters.append(Price.date >= date_from)
    if date_to:
        filters.append(Price.date <= date_to)

    query = (
        select(
            func.to_char(Price.date, "YYYY-MM").label("month"),
            func.avg(Price.usdprice).label("avg_usdprice"),
            func.count().label("count"),
        )
        .where(*filters)
        .group_by(func.to_char(Price.date, "YYYY-MM"))
        .order_by(func.to_char(Price.date, "YYYY-MM"))
    )
    result = await db.execute(query)
    rows = result.all()
    return TrendResponse(
        country=country,
        commodity_id=commodity_id,
        points=[
            TrendPoint(date=row.month, avg_usdprice=float(row.avg_usdprice), count=row.count)
            for row in rows
        ],
    )


async def get_volatility(
    db: AsyncSession,
    country: str,
    limit: int,
) -> VolatilityResponse:
    query = (
        select(
            Price.commodity_id,
            Commodity.name.label("commodity_name"),
            (func.stddev(Price.usdprice) / func.nullif(func.avg(Price.usdprice), 0)).label("cv"),
            func.avg(Price.usdprice).label("avg_usdprice"),
        )
        .join(Commodity, Price.commodity_id == Commodity.id)
        .where(Price.countryiso3 == country, Price.usdprice.is_not(None))
        .group_by(Price.commodity_id, Commodity.name)
        .having(func.stddev(Price.usdprice).is_not(None))
        .order_by(
            (func.stddev(Price.usdprice) / func.nullif(func.avg(Price.usdprice), 0)).desc()
        )
        .limit(limit)
    )
    result = await db.execute(query)
    rows = result.all()
    return VolatilityResponse(
        country=country,
        items=[
            VolatilityItem(
                commodity_id=row.commodity_id,
                commodity_name=row.commodity_name,
                cv=float(row.cv) if row.cv is not None else 0.0,
                avg_usdprice=float(row.avg_usdprice),
            )
            for row in rows
        ],
    )


async def get_regional_comparison(
    db: AsyncSession,
    commodity_id: int,
    date_from: date | None,
    date_to: date | None,
) -> RegionalComparisonResponse:
    filters = [Price.commodity_id == commodity_id, Price.usdprice.is_not(None)]
    if date_from:
        filters.append(Price.date >= date_from)
    if date_to:
        filters.append(Price.date <= date_to)

    query = (
        select(
            Price.countryiso3,
            func.avg(Price.usdprice).label("avg_usdprice"),
            func.count().label("count"),
        )
        .where(*filters)
        .group_by(Price.countryiso3)
        .order_by(func.avg(Price.usdprice).desc())
    )
    result = await db.execute(query)
    rows = result.all()
    return RegionalComparisonResponse(
        commodity_id=commodity_id,
        countries=[
            RegionalItem(
                countryiso3=row.countryiso3,
                avg_usdprice=float(row.avg_usdprice),
                count=row.count,
            )
            for row in rows
        ],
    )


async def get_market_summary(
    db: AsyncSession,
    market_id: int,
) -> MarketSummaryResponse | None:
    market_result = await db.execute(select(Market).where(Market.id == market_id))
    market = market_result.scalars().first()
    if market is None:
        return None

    stats_query = select(
        func.count().label("total"),
        func.min(Price.date).label("date_from"),
        func.max(Price.date).label("date_to"),
        func.count(Price.commodity_id.distinct()).label("commodity_count"),
    ).where(Price.market_id == market_id)
    stats_result = await db.execute(stats_query)
    stats = stats_result.one()

    # Latest price per commodity for this market
    latest_subq = (
        select(
            Price.commodity_id,
            func.max(Price.date).label("max_date"),
        )
        .where(Price.market_id == market_id)
        .group_by(Price.commodity_id)
        .subquery()
    )
    latest_query = (
        select(
            Price.commodity_id,
            Commodity.name.label("commodity_name"),
            Price.usdprice,
            Price.date,
        )
        .join(Commodity, Price.commodity_id == Commodity.id)
        .join(
            latest_subq,
            (Price.commodity_id == latest_subq.c.commodity_id)
            & (Price.date == latest_subq.c.max_date),
        )
        .where(Price.market_id == market_id)
        .order_by(Commodity.name)
    )
    latest_result = await db.execute(latest_query)
    latest_rows = latest_result.all()

    return MarketSummaryResponse(
        market_id=market_id,
        market_name=market.name,
        countryiso3=market.countryiso3,
        total_prices=stats.total,
        date_from=stats.date_from,
        date_to=stats.date_to,
        commodity_count=stats.commodity_count,
        latest_prices=[
            MarketLatestPrice(
                commodity_id=row.commodity_id,
                commodity_name=row.commodity_name,
                usdprice=float(row.usdprice) if row.usdprice is not None else None,
                date=row.date,
            )
            for row in latest_rows
        ],
    )
