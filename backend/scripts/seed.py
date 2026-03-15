"""
Seed script: fetches WFP dataset metadata from HDX, downloads missing CSV files,
then imports them into PostgreSQL.

Usage:
    python scripts/seed.py [--data-dir /path/to/data]

Environment variables:
    DATABASE_URL — async SQLAlchemy connection string (read from .env via pydantic-settings)
"""

import argparse
import asyncio
import csv
import glob
import json
import sys
import urllib.request
from pathlib import Path

import bcrypt
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Allow running from the backend/ directory
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings  # noqa: E402

METADATA_URL = (
    "https://data.humdata.org/dataset/"
    "31579af5-3895-4002-9ee3-c50857480785/download_metadata?format=json"
)

BATCH_SIZE = 1000


def _fetch_download_urls() -> dict[str, str]:
    """Return {filename: download_url} by reading the HDX dataset metadata."""
    print("  Fetching dataset metadata from HDX…")
    with urllib.request.urlopen(METADATA_URL, timeout=30) as resp:
        metadata = json.loads(resp.read())

    reference_files = {
        "wfp_commodities_global.csv",
        "wfp_currencies_global.csv",
        "wfp_markets_global.csv",
    }

    refs: dict[str, str] = {}
    price_files: dict[str, str] = {}

    for resource in metadata.get("resources", []):
        url = resource.get("download_url", "")
        if not url:
            continue
        filename = url.split("/")[-1]
        if filename in reference_files:
            refs[filename] = url
        elif filename.startswith("wfp_food_prices_global_") and filename.endswith(".csv"):
            price_files[filename] = url

    urls = {**refs, **price_files}
    print(f"  Found {len(refs)} reference file(s) + {len(price_files)} price file(s)")
    return urls


def download_missing(data_dir: Path) -> None:
    """Download any files listed in the HDX metadata that are not yet present."""
    data_dir.mkdir(parents=True, exist_ok=True)
    urls = _fetch_download_urls()

    for filename, url in sorted(urls.items()):
        dest = data_dir / filename
        if dest.exists():
            print(f"  [SKIP] {filename} already exists")
            continue
        print(f"  Downloading {filename}…", end=" ", flush=True)
        urllib.request.urlretrieve(url, dest)
        size_kb = dest.stat().st_size // 1024
        print(f"{size_kb} KB")


# ---------------------------------------------------------------------------
# Per-table seeders
# ---------------------------------------------------------------------------

async def seed_commodities(session: AsyncSession, data_dir: Path) -> int:
    csv_path = data_dir / "wfp_commodities_global.csv"
    if not csv_path.exists():
        print(f"  [SKIP] {csv_path.name} not found")
        return 0

    rows_inserted = 0
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
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
        print(f"  [SKIP] {csv_path.name} not found")
        return 0

    rows_inserted = 0
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
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
        print(f"  [SKIP] {csv_path.name} not found")
        return 0

    rows_inserted = 0
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
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
    csv_files = sorted(glob.glob(str(data_dir / "wfp_food_prices_*.csv")))
    if not csv_files:
        print(f"  [SKIP] No wfp_food_prices_*.csv files found in {data_dir}")
        return 0

    total_inserted = 0
    insert_sql = text(
        """
        INSERT INTO prices
            (date, countryiso3, admin1, admin2, market_id, commodity_id,
             category, unit, priceflag, pricetype, currency_code, price, usdprice)
        VALUES
            (:date, :countryiso3, :admin1, :admin2, :market_id, :commodity_id,
             :category, :unit, :priceflag, :pricetype, :currency_code, :price, :usdprice)
        ON CONFLICT DO NOTHING
        """
    )

    for csv_path in csv_files:
        file_inserted = 0
        batch: list[dict] = []

        with open(csv_path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
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
                    await session.execute(insert_sql, batch)
                    await session.commit()
                    file_inserted += len(batch)
                    batch = []

        if batch:
            await session.execute(insert_sql, batch)
            await session.commit()
            file_inserted += len(batch)

        print(f"  {Path(csv_path).name}: {file_inserted} rows inserted")
        total_inserted += file_inserted

    return total_inserted


async def seed_admin_user(session: AsyncSession) -> None:
    hashed = bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode()
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


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def main(data_dir: Path) -> None:
    print(f"Connecting to: {settings.DATABASE_URL}")
    print(f"Data directory: {data_dir}")
    print()

    print("Checking for missing data files…")
    download_missing(data_dir)
    print()

    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with SessionLocal() as session:
        print("Seeding commodities…")
        n = await seed_commodities(session, data_dir)
        print(f"  -> {n} rows")

        print("Seeding currencies…")
        n = await seed_currencies(session, data_dir)
        print(f"  -> {n} rows")

        print("Seeding markets…")
        n = await seed_markets(session, data_dir)
        print(f"  -> {n} rows")

        print("Seeding prices (this may take a while)…")
        n = await seed_prices(session, data_dir)
        print(f"  -> {n} total rows")

        print("Creating admin user…")
        await seed_admin_user(session)
        print("  -> admin / admin123")

    await engine.dispose()
    print("\nSeeding complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="./data", type=Path)
    args = parser.parse_args()
    asyncio.run(main(args.data_dir))
