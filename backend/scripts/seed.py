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
import logging
import sys
import urllib.request
from pathlib import Path

logger = logging.getLogger("app.seed")

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
    logger.info("Fetching dataset metadata from HDX…")
    with urllib.request.urlopen(METADATA_URL, timeout=30) as resp:
        body = resp.read()
    if not body:
        raise ValueError("HDX metadata endpoint returned an empty response")
    metadata = json.loads(body)

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
    logger.info("Found %d reference file(s) + %d price file(s)", len(refs), len(price_files))
    return urls


def download_missing(data_dir: Path) -> None:
    """Download any files listed in the HDX metadata that are not yet present."""
    data_dir.mkdir(parents=True, exist_ok=True)
    urls = _fetch_download_urls()

    for filename, url in sorted(urls.items()):
        dest = data_dir / filename
        if dest.exists():
            logger.info("[SKIP] %s already exists", filename)
            continue
        logger.info("Downloading %s…", filename)
        urllib.request.urlretrieve(url, dest)
        size_kb = dest.stat().st_size // 1024
        logger.info("  %s: %d KB", filename, size_kb)


# ---------------------------------------------------------------------------
# Per-table seeders
# ---------------------------------------------------------------------------

async def seed_commodities(session: AsyncSession, data_dir: Path) -> int:
    csv_path = data_dir / "wfp_commodities_global.csv"
    if not csv_path.exists():
        logger.warning("[SKIP] %s not found", csv_path.name)
        return 0

    batch: list[dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            batch.append({
                "id": int(row["commodity_id"]),
                "category": row.get("category", "").strip(),
                "name": row.get("commodity", "").strip(),
            })

    if batch:
        await session.execute(
            text("INSERT INTO commodities (id, category, name) VALUES (:id, :category, :name) ON CONFLICT (id) DO NOTHING"),
            batch,
        )
        await session.commit()
    return len(batch)


async def seed_currencies(session: AsyncSession, data_dir: Path) -> int:
    csv_path = data_dir / "wfp_currencies_global.csv"
    if not csv_path.exists():
        logger.warning("[SKIP] %s not found", csv_path.name)
        return 0

    batch: list[dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            batch.append({
                "code": row.get("code", "").strip(),
                "name": row.get("name", "").strip(),
            })

    if batch:
        await session.execute(
            text("INSERT INTO currencies (code, name) VALUES (:code, :name) ON CONFLICT (code) DO NOTHING"),
            batch,
        )
        await session.commit()
    return len(batch)


async def seed_markets(session: AsyncSession, data_dir: Path) -> int:
    csv_path = data_dir / "wfp_markets_global.csv"
    if not csv_path.exists():
        logger.warning("[SKIP] %s not found", csv_path.name)
        return 0

    batch: list[dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            lat = row.get("latitude", "").strip()
            lon = row.get("longitude", "").strip()
            batch.append({
                "id": int(row["market_id"]),
                "name": row.get("market", "").strip(),
                "countryiso3": row.get("countryiso3", "").strip(),
                "admin1": row.get("admin1", "").strip() or None,
                "admin2": row.get("admin2", "").strip() or None,
                "latitude": float(lat) if lat else None,
                "longitude": float(lon) if lon else None,
            })

    if batch:
        await session.execute(
            text(
                """
                INSERT INTO markets (id, name, countryiso3, admin1, admin2, latitude, longitude)
                VALUES (:id, :name, :countryiso3, :admin1, :admin2, :latitude, :longitude)
                ON CONFLICT (id) DO NOTHING
                """
            ),
            batch,
        )
        await session.commit()
    return len(batch)


async def seed_prices(session: AsyncSession, data_dir: Path) -> int:
    csv_files = sorted(glob.glob(str(data_dir / "wfp_food_prices_*.csv")))
    if not csv_files:
        logger.warning("[SKIP] No wfp_food_prices_*.csv files found in %s", data_dir)
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

        logger.info("%s: %d rows inserted", Path(csv_path).name, file_inserted)
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
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    logger.info("Connecting to: %s", settings.DATABASE_URL)
    logger.info("Data directory: %s", data_dir)

    logger.info("Checking for missing data files…")
    download_missing(data_dir)

    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with SessionLocal() as session:
        logger.info("Seeding commodities…")
        n = await seed_commodities(session, data_dir)
        logger.info("  -> %d rows", n)

        logger.info("Seeding currencies…")
        n = await seed_currencies(session, data_dir)
        logger.info("  -> %d rows", n)

        logger.info("Seeding markets…")
        n = await seed_markets(session, data_dir)
        logger.info("  -> %d rows", n)

        logger.info("Seeding prices (this may take a while)…")
        n = await seed_prices(session, data_dir)
        logger.info("  -> %d total rows", n)

        logger.info("Creating admin user…")
        await seed_admin_user(session)
        logger.info("  -> admin / admin123")

    await engine.dispose()
    logger.info("Seeding complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="./data", type=Path)
    args = parser.parse_args()
    asyncio.run(main(args.data_dir))
