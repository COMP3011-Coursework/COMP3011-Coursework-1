from typing import Optional

from pydantic import BaseModel, ConfigDict


class CountryResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"example": {"countryiso3": "ETH", "count": 4823}}
    )

    countryiso3: str
    count: int


class CommodityResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {"id": 10, "category": "cereals and tubers", "name": "Maize"}
        },
    )

    id: int
    category: str
    name: str


class MarketResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Addis Ababa",
                "countryiso3": "ETH",
                "admin1": "Addis Ababa",
                "admin2": None,
                "latitude": 9.025,
                "longitude": 38.747,
            }
        },
    )

    id: int
    name: str
    countryiso3: str
    admin1: Optional[str] = None
    admin2: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class CurrencyResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={"example": {"code": "ETB", "name": "Ethiopian Birr"}},
    )

    code: str
    name: str
