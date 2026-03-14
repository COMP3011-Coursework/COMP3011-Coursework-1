from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

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


@router.get("/trends", response_model=TrendResponse)
async def get_trends(
    country: str,
    commodity_id: int,
    date_from: date | None = None,
    date_to: date | None = None,
    db: AsyncSession = Depends(get_db),
) -> TrendResponse:
    return await analytics_service.get_price_trends(db, country, commodity_id, date_from, date_to)


@router.get("/volatility", response_model=VolatilityResponse)
async def get_volatility(
    country: str,
    limit: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
) -> VolatilityResponse:
    return await analytics_service.get_volatility(db, country, limit)


@router.get("/regional-comparison", response_model=RegionalComparisonResponse)
async def get_regional_comparison(
    commodity_id: int,
    date_from: date | None = None,
    date_to: date | None = None,
    db: AsyncSession = Depends(get_db),
) -> RegionalComparisonResponse:
    return await analytics_service.get_regional_comparison(db, commodity_id, date_from, date_to)


@router.get("/crisis-scores", response_model=list[CrisisScoreResponse])
async def get_crisis_scores(
    db: AsyncSession = Depends(get_db),
) -> list[CrisisScoreResponse]:
    return await compute_crisis_scores(db)


@router.get("/crisis-scores/{country}", response_model=CrisisScoreResponse)
async def get_crisis_score_by_country(
    country: str,
    db: AsyncSession = Depends(get_db),
) -> CrisisScoreResponse:
    results = await compute_crisis_scores(db, country=country)
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No data found for country '{country}'",
        )
    return results[0]


@router.get("/markets/{market_id}/summary", response_model=MarketSummaryResponse)
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
