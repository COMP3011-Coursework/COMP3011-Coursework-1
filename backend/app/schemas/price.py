from datetime import date as Date
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PriceBase(BaseModel):
    date: Date
    countryiso3: str = Field(min_length=3, max_length=3)
    admin1: Optional[str] = None
    admin2: Optional[str] = None
    market_id: int
    commodity_id: int
    category: Optional[str] = None
    unit: Optional[str] = None
    priceflag: Optional[str] = None
    pricetype: Optional[str] = None
    currency_code: str = Field(min_length=1, max_length=10)
    price: Optional[float] = Field(default=None, ge=0)
    usdprice: Optional[float] = Field(default=None, ge=0)


class PriceCreate(PriceBase):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "date": "2024-01-15",
                "countryiso3": "ETH",
                "admin1": "Oromia",
                "admin2": "Jimma",
                "market_id": 1,
                "commodity_id": 10,
                "category": "cereals and tubers",
                "unit": "KG",
                "priceflag": "actual",
                "pricetype": "Retail",
                "currency_code": "ETB",
                "price": 45.50,
                "usdprice": 0.82,
            }
        }
    )


class PriceUpdate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "price": 48.00,
                "usdprice": 0.86,
            }
        }
    )

    date: Optional[Date] = None
    countryiso3: Optional[str] = Field(default=None, min_length=3, max_length=3)
    admin1: Optional[str] = None
    admin2: Optional[str] = None
    market_id: Optional[int] = None
    commodity_id: Optional[int] = None
    category: Optional[str] = None
    unit: Optional[str] = None
    priceflag: Optional[str] = None
    pricetype: Optional[str] = None
    currency_code: Optional[str] = Field(default=None, min_length=1, max_length=10)
    price: Optional[float] = Field(default=None, ge=0)
    usdprice: Optional[float] = Field(default=None, ge=0)


class PriceResponse(PriceBase):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1001,
                "date": "2024-01-15",
                "countryiso3": "ETH",
                "admin1": "Oromia",
                "admin2": "Jimma",
                "market_id": 1,
                "commodity_id": 10,
                "category": "cereals and tubers",
                "unit": "KG",
                "priceflag": "actual",
                "pricetype": "Retail",
                "currency_code": "ETB",
                "price": 45.50,
                "usdprice": 0.82,
                "created_at": "2024-01-15T12:00:00Z",
                "updated_at": "2024-01-15T12:00:00Z",
            }
        },
    )

    id: int
    created_at: datetime
    updated_at: datetime


class PriceListResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "id": 1001,
                        "date": "2024-01-15",
                        "countryiso3": "ETH",
                        "market_id": 1,
                        "commodity_id": 10,
                        "currency_code": "ETB",
                        "price": 45.50,
                        "usdprice": 0.82,
                        "created_at": "2024-01-15T12:00:00Z",
                        "updated_at": "2024-01-15T12:00:00Z",
                    }
                ],
                "total": 4823,
                "page": 1,
                "page_size": 50,
            }
        }
    )

    items: list[PriceResponse]
    total: int
    page: int
    page_size: int
