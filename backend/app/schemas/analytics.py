from datetime import date

from pydantic import BaseModel, ConfigDict


class TrendPoint(BaseModel):
    date: str  # "YYYY-MM"
    avg_usdprice: float
    count: int


class TrendResponse(BaseModel):
    country: str
    commodity_id: int
    points: list[TrendPoint]


class VolatilityItem(BaseModel):
    commodity_id: int
    commodity_name: str
    cv: float  # coefficient of variation (stddev / mean)
    avg_usdprice: float


class VolatilityResponse(BaseModel):
    country: str
    items: list[VolatilityItem]


class RegionalItem(BaseModel):
    countryiso3: str
    avg_usdprice: float
    count: int


class RegionalComparisonResponse(BaseModel):
    commodity_id: int
    countries: list[RegionalItem]


class CrisisScoreResponse(BaseModel):
    countryiso3: str
    crisis_score: float
    severity: str  # stable | moderate | high | critical
    volatility_score: float
    trend_score: float
    breadth_score: float


class MarketLatestPrice(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    commodity_id: int
    commodity_name: str
    usdprice: float | None
    date: date


class MarketSummaryResponse(BaseModel):
    market_id: int
    market_name: str
    countryiso3: str
    total_prices: int
    date_from: date | None
    date_to: date | None
    commodity_count: int
    latest_prices: list[MarketLatestPrice]
