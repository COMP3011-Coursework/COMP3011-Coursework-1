from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import cache
from app.database import get_db
from app.schemas.analytics import (
    CrisisScoreResponse,
    MarketSummaryResponse,
    RegionalComparisonResponse,
    TrendResponse,
    VolatilityResponse,
)
from app.services import analytics as analytics_service
from app.services.crisis_score import compute_crisis_scores

router = APIRouter(prefix="/analytics", tags=["analytics"])

_404_country = {"description": "No data found for the given country code"}
_404_market = {"description": "Market not found"}


@router.get(
    "/trends",
    response_model=TrendResponse,
    summary="Monthly price trend for a commodity in a country",
    description=(
        "Return monthly average USD prices for the specified country and commodity. "
        "Optionally narrow the window with `date_from` / `date_to`. "
        "Returns 404 if no data exists for the combination."
    ),
    response_description="Time series of monthly average prices",
    responses={404: _404_country},
)
async def get_trends(
    country: str = Query(description="ISO 3166-1 alpha-3 country code, e.g. `ETH`"),
    commodity_id: int = Query(description="Commodity ID from `/commodities`"),
    date_from: date | None = Query(default=None, description="Inclusive start date (YYYY-MM-DD)"),
    date_to: date | None = Query(default=None, description="Inclusive end date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
) -> TrendResponse:
    if cache.wfp_countries and country not in cache.wfp_countries:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No data found for country '{country}'",
        )
    result = await analytics_service.get_price_trends(db, country, commodity_id, date_from, date_to)
    if not result.points:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No price data found for country '{country}' and commodity {commodity_id}",
        )
    return result


@router.get(
    "/volatility",
    response_model=VolatilityResponse,
    summary="Price volatility ranking for a country",
    description=(
        "Return the top-N commodities ranked by coefficient of variation (CV = stddev / mean) "
        "of their USD price in the given country. Higher CV indicates more volatile pricing."
    ),
    response_description="List of commodities sorted by volatility (highest first)",
    responses={404: _404_country},
)
async def get_volatility(
    country: str = Query(description="ISO 3166-1 alpha-3 country code, e.g. `ETH`"),
    limit: int = Query(default=10, ge=1, le=50, description="Maximum number of commodities to return"),
    db: AsyncSession = Depends(get_db),
) -> VolatilityResponse:
    if cache.wfp_countries and country not in cache.wfp_countries:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No data found for country '{country}'",
        )
    return await analytics_service.get_volatility(db, country, limit)


@router.get(
    "/regional-comparison",
    response_model=RegionalComparisonResponse,
    summary="Compare commodity prices across countries",
    description=(
        "Return the average USD price of a single commodity in every country that has recorded it, "
        "sorted highest-to-lowest. Useful for spotting regional price disparities."
    ),
    response_description="Average USD price per country, sorted descending",
)
async def get_regional_comparison(
    commodity_id: int = Query(description="Commodity ID from `/commodities`"),
    date_from: date | None = Query(default=None, description="Inclusive start date (YYYY-MM-DD)"),
    date_to: date | None = Query(default=None, description="Inclusive end date (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
) -> RegionalComparisonResponse:
    return await analytics_service.get_regional_comparison(db, commodity_id, date_from, date_to)


@router.get(
    "/crisis-scores",
    response_model=list[CrisisScoreResponse],
    summary="Food crisis scores for all countries",
    description=(
        "Compute a composite food-crisis score (0–100) for every country using a 12-month trailing window. "
        "The score blends volatility (40%), price trend (35%), and commodity breadth (25%). "
        "Severity bands: **stable** < 25 ≤ **moderate** < 50 ≤ **high** < 75 ≤ **critical**."
    ),
    response_description="Crisis scores for all countries with data, sorted by score descending",
)
async def get_crisis_scores(
    db: AsyncSession = Depends(get_db),
) -> list[CrisisScoreResponse]:
    return await compute_crisis_scores(db)


@router.get(
    "/crisis-scores/{country}",
    response_model=CrisisScoreResponse,
    summary="Food crisis score for a single country",
    description="Return the composite food-crisis score for the given ISO 3166-1 alpha-3 country code.",
    response_description="Crisis score breakdown for the requested country",
    responses={404: _404_country},
)
async def get_crisis_score_by_country(
    country: str,
    db: AsyncSession = Depends(get_db),
) -> CrisisScoreResponse:
    if cache.wfp_countries and country not in cache.wfp_countries:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No data found for country '{country}'",
        )
    results = await compute_crisis_scores(db, country=country)
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No data found for country '{country}'",
        )
    return results[0]


@router.get(
    "/markets/{market_id}/summary",
    response_model=MarketSummaryResponse,
    summary="Market summary with latest prices",
    description=(
        "Return aggregate statistics and the most recent price for each commodity "
        "recorded at the specified market."
    ),
    response_description="Market metadata, date range, and latest price per commodity",
    responses={404: _404_market},
)
async def get_market_summary(
    market_id: int,
    db: AsyncSession = Depends(get_db),
) -> MarketSummaryResponse:
    summary = await analytics_service.get_market_summary(db, market_id)
    if summary is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Market {market_id} not found",
        )
    return summary
