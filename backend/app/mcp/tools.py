from datetime import date, timedelta

from fastmcp import FastMCP
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.commodity import Commodity
from app.services import analytics as analytics_service
from app.services.crisis_score import compute_crisis_scores

mcp = FastMCP("Global Food Price Monitor")


async def _commodity_id(db, name: str) -> int:
    row = await db.execute(
        select(Commodity.id).where(Commodity.name.ilike(name)).limit(1)
    )
    result = row.scalar()
    if result is None:
        raise ValueError(f"Commodity '{name}' not found")
    return result


@mcp.tool()
async def get_global_crisis_overview() -> list[dict]:
    """Return the top 20 countries ranked by food price crisis score.

    Each entry includes: countryiso3, crisis_score (0-100), severity
    (stable/moderate/high/critical), and component scores for volatility,
    trend, and breadth.
    """
    async with AsyncSessionLocal() as db:
        scores = await compute_crisis_scores(db)
    return [
        {
            "countryiso3": s.countryiso3,
            "crisis_score": s.crisis_score,
            "severity": s.severity,
            "volatility_score": s.volatility_score,
            "trend_score": s.trend_score,
            "breadth_score": s.breadth_score,
        }
        for s in scores[:20]
    ]


@mcp.tool()
async def get_crisis_summary(country: str) -> dict:
    """Return a full crisis breakdown for a single country (ISO3 code, e.g. 'ETH').

    Includes the crisis score, severity, component breakdown, and the top 5
    most price-volatile commodities.
    """
    async with AsyncSessionLocal() as db:
        scores = await compute_crisis_scores(db, country=country)
        if not scores:
            raise ValueError(f"No data found for country '{country}'")
        s = scores[0]
        volatility = await analytics_service.get_volatility(db, country, limit=5)

    return {
        "countryiso3": s.countryiso3,
        "crisis_score": s.crisis_score,
        "severity": s.severity,
        "volatility_score": s.volatility_score,
        "trend_score": s.trend_score,
        "breadth_score": s.breadth_score,
        "top_volatile_commodities": [
            {
                "commodity_name": item.commodity_name,
                "cv": item.cv,
                "avg_usdprice": item.avg_usdprice,
            }
            for item in volatility.items
        ],
    }


@mcp.tool()
async def get_price_trends(country: str, commodity: str, months: int = 24) -> list[dict]:
    """Return monthly average USD prices for a commodity in a country.

    Args:
        country: ISO3 country code (e.g. 'KEN').
        commodity: Commodity name (e.g. 'Wheat', 'Rice').
        months: Number of months of history to return (default 24).

    Returns a list of {date (YYYY-MM), avg_usdprice, count} dicts.
    """
    date_from = date.today() - timedelta(days=months * 30)
    async with AsyncSessionLocal() as db:
        commodity_id = await _commodity_id(db, commodity)
        trends = await analytics_service.get_price_trends(
            db, country, commodity_id, date_from, None
        )
    return [
        {"date": p.date, "avg_usdprice": p.avg_usdprice, "count": p.count}
        for p in trends.points
    ]


@mcp.tool()
async def compare_regional_prices(commodity: str) -> list[dict]:
    """Compare average USD prices for a commodity across all countries with data.

    Args:
        commodity: Commodity name (e.g. 'Maize', 'Sugar').

    Returns a list of {countryiso3, avg_usdprice, count} dicts, sorted by price descending.
    """
    async with AsyncSessionLocal() as db:
        commodity_id = await _commodity_id(db, commodity)
        comparison = await analytics_service.get_regional_comparison(
            db, commodity_id, None, None
        )
    return [
        {"countryiso3": item.countryiso3, "avg_usdprice": item.avg_usdprice, "count": item.count}
        for item in comparison.countries
    ]


@mcp.tool()
async def get_volatile_commodities(country: str, limit: int = 10) -> list[dict]:
    """Return the most price-volatile commodities in a country, ranked by coefficient of variation.

    Args:
        country: ISO3 country code (e.g. 'SOM').
        limit: Max number of commodities to return (default 10, max 50).

    Returns a list of {commodity_name, cv, avg_usdprice} dicts.
    """
    limit = min(max(limit, 1), 50)
    async with AsyncSessionLocal() as db:
        volatility = await analytics_service.get_volatility(db, country, limit)
    return [
        {
            "commodity_name": item.commodity_name,
            "cv": item.cv,
            "avg_usdprice": item.avg_usdprice,
        }
        for item in volatility.items
    ]
