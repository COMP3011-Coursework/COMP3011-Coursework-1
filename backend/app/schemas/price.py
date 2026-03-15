from datetime import date as Date
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PriceBase(BaseModel):
    date: Date
    countryiso3: str
    admin1: Optional[str] = None
    admin2: Optional[str] = None
    market_id: int
    commodity_id: int
    category: Optional[str] = None
    unit: Optional[str] = None
    priceflag: Optional[str] = None
    pricetype: Optional[str] = None
    currency_code: str
    price: Optional[float] = None
    usdprice: Optional[float] = None


class PriceCreate(PriceBase):
    pass


class PriceUpdate(BaseModel):
    date: Optional[Date] = None
    countryiso3: Optional[str] = None
    admin1: Optional[str] = None
    admin2: Optional[str] = None
    market_id: Optional[int] = None
    commodity_id: Optional[int] = None
    category: Optional[str] = None
    unit: Optional[str] = None
    priceflag: Optional[str] = None
    pricetype: Optional[str] = None
    currency_code: Optional[str] = None
    price: Optional[float] = None
    usdprice: Optional[float] = None


class PriceResponse(PriceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class PriceListResponse(BaseModel):
    items: list[PriceResponse]
    total: int
    page: int
    page_size: int
