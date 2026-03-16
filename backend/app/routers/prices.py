from datetime import date
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_active_user
from app.database import get_db
from app.models.currency import Currency
from app.models.price import Price
from app.models.user import User
from app.schemas.price import PriceCreate, PriceListResponse, PriceResponse, PriceUpdate

router = APIRouter(prefix="/prices", tags=["prices"])


async def _validate_currency(code: str, db: AsyncSession) -> None:
    result = await db.execute(select(Currency).where(Currency.code == code))
    if result.scalars().first() is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unknown currency code: {code!r}",
        )


@router.post("", response_model=PriceResponse, status_code=status.HTTP_201_CREATED)
async def create_price(
    price_in: PriceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> PriceResponse:
    await _validate_currency(price_in.currency_code, db)
    price = Price(**price_in.model_dump())
    db.add(price)
    await db.flush()
    await db.refresh(price)
    return price


@router.get("", response_model=PriceListResponse)
async def list_prices(
    db: AsyncSession = Depends(get_db),
    country: Optional[str] = None,
    commodity_id: Optional[int] = None,
    market_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    page: int = 1,
    page_size: int = Query(default=50, le=200),
) -> PriceListResponse:
    filters = []
    if country is not None:
        filters.append(Price.countryiso3 == country)
    if commodity_id is not None:
        filters.append(Price.commodity_id == commodity_id)
    if market_id is not None:
        filters.append(Price.market_id == market_id)
    if date_from is not None:
        filters.append(Price.date >= date_from)
    if date_to is not None:
        filters.append(Price.date <= date_to)

    count_query = select(func.count()).select_from(Price)
    if filters:
        count_query = count_query.where(*filters)
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    offset = (page - 1) * page_size
    items_query = select(Price)
    if filters:
        items_query = items_query.where(*filters)
    items_query = items_query.offset(offset).limit(page_size)
    items_result = await db.execute(items_query)
    items = items_result.scalars().all()

    return PriceListResponse(items=list(items), total=total, page=page, page_size=page_size)


@router.get("/{price_id}", response_model=PriceResponse)
async def get_price(
    price_id: int,
    db: AsyncSession = Depends(get_db),
) -> PriceResponse:
    result = await db.execute(select(Price).where(Price.id == price_id))
    price = result.scalars().first()
    if price is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Price not found")
    return price


@router.put("/{price_id}", response_model=PriceResponse)
async def update_price(
    price_id: int,
    price_in: PriceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> PriceResponse:
    result = await db.execute(select(Price).where(Price.id == price_id))
    price = result.scalars().first()
    if price is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Price not found")
    update_data = price_in.model_dump(exclude_none=True)
    if "currency_code" in update_data:
        await _validate_currency(update_data["currency_code"], db)
    for field, value in update_data.items():
        setattr(price, field, value)
    await db.flush()
    await db.refresh(price)
    return price


@router.delete("/{price_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_price(
    price_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    result = await db.execute(select(Price).where(Price.id == price_id))
    price = result.scalars().first()
    if price is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Price not found")
    await db.delete(price)
