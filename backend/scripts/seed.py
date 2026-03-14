"""
Seed script: imports CSV data from WFP food price dataset into PostgreSQL.

Usage:
    DATA_DIR=./data python scripts/seed.py

Environment variables:
    DATA_DIR  — directory containing WFP CSV files (default: ./data)
    DATABASE_URL — async SQLAlchemy connection string (read from .env via pydantic-settings)
"""

import asyncio
import csv
import glob
import os
import sys
from pathlib import Path

from passlib.context import CryptContext
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Allow running from the backend/ directory
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings  # noqa: E402

DATA_DIR = Path(os.environ.get("DATA_DIR", "./data"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

BATCH_SIZE = 1000


async def seed_commodities(session: AsyncSession, data_dir: Path) -> int:
    csv_path = data_dir / "wfp_commodities_global.csv"
    if not csv_path.exists():
        print(f"  [SKIP] {csv_path} not found")
        return 0

    rows_inserted = 0
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            await session.execute(
                text(
                    """
                    INSERT INTO commodities (id, category, name)
                    VALUES (:id, :category, :name)
                    ON CONFLICT (id) DO NOTHING
                    """
                ),
                {
                    "id": int(row["commodity_id"]),
                    "category": row.get("category", "").strip(),
                    "name": row.get("commodity", "").strip(),
                },
            )
            rows_inserted += 1

    await session.commit()
    return rows_inserted


async def seed_currencies(session: AsyncSession, data_dir: Path) -> int:
    csv_path = data_dir / "wfp_currencies_global.csv"
    if not csv_path.exists():
        print(f"  [SKIP] {csv_path} not found")
        return 0

    rows_inserted = 0
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            await session.execute(
                text(
                    """
                    INSERT INTO currencies (code, name)
                    VALUES (:code, :name)
                    ON CONFLICT (code) DO NOTHING
                    """
                ),
                {
                    "code": row.get("code", "").strip(),
                    "name": row.get("name", "").strip(),
                },
            )
            rows_inserted += 1

    await session.commit()
    return rows_inserted


async def seed_markets(session: AsyncSession, data_dir: Path) -> int:
    csv_path = data_dir / "wfp_markets_global.csv"
    if not csv_path.exists():
        print(f"  [SKIP] {csv_path} not found")
        return 0

    rows_inserted = 0
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            lat = row.get("latitude", "").strip()
            lon = row.get("longitude", "").strip()
            await session.execute(
                text(
                    """
                    INSERT INTO markets (id, name, countryiso3, admin1, admin2, latitude, longitude)
                    VALUES (:id, :name, :countryiso3, :admin1, :admin2, :latitude, :longitude)
                    ON CONFLICT (id) DO NOTHING
                    """
                ),
                {
                    "id": int(row["market_id"]),
                    "name": row.get("market", "").strip(),
                    "countryiso3": row.get("countryiso3", "").strip(),
                    "admin1": row.get("admin1", "").strip() or None,
                    "admin2": row.get("admin2", "").strip() or None,
                    "latitude": float(lat) if lat else None,
                    "longitude": float(lon) if lon else None,
                },
            )
            rows_inserted += 1

    await session.commit()
    return rows_inserted


async def seed_prices(session: AsyncSession, data_dir: Path) -> int:
    pattern = str(data_dir / "wfp_food_prices_*.csv")
    csv_files = sorted(glob.glob(pattern))

    if not csv_files:
        print(f"  [SKIP] No files matching {pattern}")
        return 0

    total_inserted = 0

    for csv_path in csv_files:
        file_inserted = 0
        batch: list[dict] = []

        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                price_val = row.get("price", "").strip()
                usdprice_val = row.get("usdprice", "").strip()

                batch.append(
                    {
                        "date": row.get("date", "").strip(),
                        "countryiso3": row.get("countryiso3", "").strip(),
                        "admin1": row.get("admin1", "").strip() or None,
                        "admin2": row.get("admin2", "").strip() or None,
                        "market_id": int(row["market_id"]),
                        "commodity_id": int(row["commodity_id"]),
                        "category": row.get("category", "").strip() or None,
                        "unit": row.get("unit", "").strip() or None,
                        "priceflag": row.get("priceflag", "").strip() or None,
                        "pricetype": row.get("pricetype", "").strip() or None,
                        "currency_code": row.get("currency", "").strip(),
                        "price": float(price_val) if price_val else None,
                        "usdprice": float(usdprice_val) if usdprice_val else None,
                    }
                )

                if len(batch) >= BATCH_SIZE:
                    await session.execute(
                        text(
                            """
                            INSERT INTO prices
                                (date, countryiso3, admin1, admin2, market_id, commodity_id,
                                 category, unit, priceflag, pricetype, currency_code,
                                 price, usdprice)
                            VALUES
                                (:date, :countryiso3, :admin1, :admin2, :market_id, :commodity_id,
                                 :category, :unit, :priceflag, :pricetype, :currency_code,
                                 :price, :usdprice)
                            """
                        ),
                        batch,
                    )
                    await session.commit()
                    file_inserted += len(batch)
                    batch = []

            # Insert remaining rows
            if batch:
                await session.execute(
                    text(
                        """
                        INSERT INTO prices
                            (date, countryiso3, admin1, admin2, market_id, commodity_id,
                             category, unit, priceflag, pricetype, currency_code,
                             price, usdprice)
                        VALUES
                            (:date, :countryiso3, :admin1, :admin2, :market_id, :commodity_id,
                             :category, :unit, :priceflag, :pricetype, :currency_code,
                             :price, :usdprice)
                        ON CONFLICT DO NOTHING
                        """
                    ),
                    batch,
                )
                await session.commit()
                file_inserted += len(batch)

        print(f"  {Path(csv_path).name}: {file_inserted} rows inserted")
        total_inserted += file_inserted

    return total_inserted


async def seed_admin_user(session: AsyncSession) -> None:
    hashed = pwd_context.hash("admin123")
    await session.execute(
        text(
            """
            INSERT INTO users (username, email, hashed_password, is_active)
            VALUES (:username, :email, :hashed_password, :is_active)
            ON CONFLICT (username) DO NOTHING
            """
        ),
        {
            "username": "admin",
            "email": "admin@example.com",
            "hashed_password": hashed,
            "is_active": True,
        },
    )
    await session.commit()


async def main() -> None:
    print(f"Connecting to database: {settings.DATABASE_URL}")
    print(f"Reading data from: {DATA_DIR}")
    print()

    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with SessionLocal() as session:
        print("Seeding commodities...")
        n = await seed_commodities(session, DATA_DIR)
        print(f"  -> {n} rows processed")

        print("Seeding currencies...")
        n = await seed_currencies(session, DATA_DIR)
        print(f"  -> {n} rows processed")

        print("Seeding markets...")
        n = await seed_markets(session, DATA_DIR)
        print(f"  -> {n} rows processed")

        print("Seeding prices (this may take a while)...")
        n = await seed_prices(session, DATA_DIR)
        print(f"  -> {n} total price rows inserted")

        print("Creating admin user...")
        await seed_admin_user(session)
        print("  -> admin user created (username: admin, password: admin123)")

    await engine.dispose()
    print()
    print("Seeding complete.")


if __name__ == "__main__":
    asyncio.run(main())
