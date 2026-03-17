from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict


class TrendPoint(BaseModel):
    date: str  # "YYYY-MM"
    avg_usdprice: float
    count: int


class TrendResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "country": "ETH",
                "commodity_id": 10,
                "points": [
                    {"date": "2023-01", "avg_usdprice": 0.74, "count": 12},
                    {"date": "2023-06", "avg_usdprice": 0.79, "count": 15},
                    {"date": "2024-01", "avg_usdprice": 0.82, "count": 14},
                ],
            }
        }
    )

    country: str
    commodity_id: int
    points: list[TrendPoint]


class VolatilityItem(BaseModel):
    commodity_id: int
    commodity_name: str
    cv: float  # coefficient of variation (stddev / mean)
    avg_usdprice: float


class VolatilityResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "country": "ETH",
                "items": [
                    {
                        "commodity_id": 71,
                        "commodity_name": "Fuel (diesel)",
                        "cv": 0.34,
                        "avg_usdprice": 1.12,
                    },
                    {
                        "commodity_id": 10,
                        "commodity_name": "Maize",
                        "cv": 0.18,
                        "avg_usdprice": 0.82,
                    },
                ],
            }
        }
    )

    country: str
    items: list[VolatilityItem]


class RegionalItem(BaseModel):
    countryiso3: str
    avg_usdprice: float
    count: int


class RegionalComparisonResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "commodity_id": 10,
                "countries": [
                    {"countryiso3": "SOM", "avg_usdprice": 1.45, "count": 320},
                    {"countryiso3": "ETH", "avg_usdprice": 0.82, "count": 4823},
                    {"countryiso3": "UGA", "avg_usdprice": 0.61, "count": 1102},
                ],
            }
        }
    )

    commodity_id: int
    countries: list[RegionalItem]


class CrisisScoreResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "countryiso3": "SOM",
                "crisis_score": 72.4,
                "severity": "high",
                "volatility_score": 68.1,
                "trend_score": 81.3,
                "breadth_score": 55.9,
            }
        }
    )

    countryiso3: str
    crisis_score: float
    severity: Literal["stable", "moderate", "high", "critical"]
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
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "market_id": 1,
                "market_name": "Addis Ababa",
                "countryiso3": "ETH",
                "total_prices": 1240,
                "date_from": "2019-01-15",
                "date_to": "2024-01-15",
                "commodity_count": 8,
                "latest_prices": [
                    {
                        "commodity_id": 10,
                        "commodity_name": "Maize",
                        "usdprice": 0.82,
                        "date": "2024-01-15",
                    },
                    {
                        "commodity_id": 71,
                        "commodity_name": "Fuel (diesel)",
                        "usdprice": 1.12,
                        "date": "2024-01-15",
                    },
                ],
            }
        }
    )

    market_id: int
    market_name: str
    countryiso3: str
    total_prices: int
    date_from: date | None
    date_to: date | None
    commodity_count: int
    latest_prices: list[MarketLatestPrice]
