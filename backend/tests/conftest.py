"""Shared pytest fixtures for the backend test suite.

Tests require a running PostgreSQL instance. Set TEST_DATABASE_URL or the
default postgresql+psycopg://postgres:postgres@localhost:5432/food_monitor_test
will be used.
"""

import os
from datetime import date, timedelta

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.auth.password import hash_password
from app.database import Base, get_db
from app.main import app
from app.models.commodity import Commodity
from app.models.currency import Currency
from app.models.market import Market
from app.models.price import Price
from app.models.user import User

# ---------------------------------------------------------------------------
# Test database URL
# ---------------------------------------------------------------------------
_default_url = "postgresql+psycopg://postgres:postgres@localhost:5432/food_monitor_test"
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", _default_url)


# ---------------------------------------------------------------------------
# Session-scoped: create / drop tables once per test run
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


# ---------------------------------------------------------------------------
# Function-scoped: isolated DB session per test via transaction rollback
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture
async def db(test_engine):
    """Each test runs inside a transaction that is rolled back afterwards."""
    async with test_engine.connect() as conn:
        await conn.begin()
        session = AsyncSession(
            bind=conn,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )
        yield session
        await session.close()
        await conn.rollback()


# ---------------------------------------------------------------------------
# HTTP client with overridden DB dependency
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture
async def client(db: AsyncSession):
    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Reference data (minimal rows required by FK constraints)
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture
async def currency(db: AsyncSession) -> Currency:
    cur = Currency(code="USD", name="US Dollar")
    db.add(cur)
    await db.flush()
    return cur


@pytest_asyncio.fixture
async def commodity(db: AsyncSession) -> Commodity:
    comm = Commodity(id=9001, category="Cereals and Tubers", name="Test Wheat")
    db.add(comm)
    await db.flush()
    return comm


@pytest_asyncio.fixture
async def market(db: AsyncSession) -> Market:
    mkt = Market(id=9001, name="Test Market", countryiso3="TST")
    db.add(mkt)
    await db.flush()
    return mkt


# ---------------------------------------------------------------------------
# Auth fixtures
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture
async def test_user(db: AsyncSession) -> tuple[User, str]:
    plain = "testpassword123"
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password(plain),
    )
    db.add(user)
    await db.flush()
    return user, plain


@pytest_asyncio.fixture
async def auth_headers(test_user, client: AsyncClient) -> dict[str, str]:
    _, plain = test_user
    resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": plain},
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Price payload helper
# ---------------------------------------------------------------------------
def price_payload(
    commodity_id: int,
    market_id: int,
    country: str = "TST",
    usdprice: float = 1.50,
    d: date | None = None,
) -> dict:
    return {
        "date": str(d or date.today()),
        "countryiso3": country,
        "market_id": market_id,
        "commodity_id": commodity_id,
        "currency_code": "USD",
        "usdprice": usdprice,
        "price": usdprice,
        "unit": "KG",
    }


# ---------------------------------------------------------------------------
# Analytics seed: session-scoped so data persists across analytics tests.
# Insert enough rows for the CTE queries (COUNT(*) >= 3 required).
# Two countries × 3 commodities × 6 monthly observations.
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture(scope="session")
async def analytics_seed(test_engine):
    """Insert stable reference + price data for analytics tests."""
    async with test_engine.connect() as conn:
        async with conn.begin():
            session = AsyncSession(bind=conn, expire_on_commit=False)

            # Reference rows
            session.add(Currency(code="USD", name="US Dollar"))
            for cid, cname in [(1001, "Rice"), (1002, "Maize"), (1003, "Wheat")]:
                session.add(Commodity(id=cid, category="Cereals", name=cname))
            for mid, iso in [(2001, "AAA"), (2002, "BBB")]:
                session.add(Market(id=mid, name=f"Market {mid}", countryiso3=iso))
            await session.flush()

            # 6 monthly price observations per country/commodity pair
            base_date = date.today().replace(day=1)
            for month_offset in range(6):
                obs_date = (base_date - timedelta(days=30 * month_offset)).replace(day=1)
                for iso, mid in [("AAA", 2001), ("BBB", 2002)]:
                    for cid, base_price in [(1001, 1.0), (1002, 2.0), (1003, 3.0)]:
                        # Add small variation so stddev > 0
                        variation = 0.1 * month_offset
                        session.add(
                            Price(
                                date=obs_date,
                                countryiso3=iso,
                                market_id=mid,
                                commodity_id=cid,
                                currency_code="USD",
                                usdprice=base_price + variation,
                                price=base_price + variation,
                                unit="KG",
                            )
                        )
            await session.flush()
            await conn.commit()

    yield {"countries": ["AAA", "BBB"], "commodity_ids": [1001, 1002, 1003], "market_ids": [2001, 2002]}
