from typing import Optional

from pydantic import BaseModel, ConfigDict


class CountryResponse(BaseModel):
    countryiso3: str
    count: int


class CommodityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category: str
    name: str


class MarketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    countryiso3: str
    admin1: Optional[str] = None
    admin2: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class CurrencyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    name: str
