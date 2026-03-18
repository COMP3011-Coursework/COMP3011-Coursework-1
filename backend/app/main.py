import asyncio
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import settings
from app.database import AsyncSessionLocal, Base, engine
from app.mcp.tools import mcp as mcp_server
from app.models import Commodity, Currency, Market, Price, User  # noqa: F401 — registers metadata
from app.routers import analytics as analytics_router_module
from app.routers import auth as auth_router_module
from app.routers import prices as prices_router_module
from app.routers import reference as reference_router_module

logger = logging.getLogger(__name__)
_app_logger = logging.getLogger("app")

mcp_http_app = mcp_server.http_app(path="/")


async def _auto_seed() -> None:
    """Download data files if missing, then seed the database if it is empty."""
    from scripts.seed import (  # type: ignore[import]
        download_missing,
        seed_admin_user,
        seed_commodities,
        seed_currencies,
        seed_markets,
        seed_prices,
    )

    data_dir = Path(os.environ.get("DATA_DIR", "./data"))

    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM commodities"))
        count = result.scalar()

    if count and count > 0:
        return  # already seeded

    logger.info("Database is empty — downloading data files and seeding from %s", data_dir)
    loop = asyncio.get_running_loop()
    try:
        await loop.run_in_executor(None, download_missing, data_dir)
    except Exception as exc:
        logger.warning("Could not download data files: %s — proceeding with any local files", exc)
    async with AsyncSessionLocal() as session:
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

    logger.info("Seeding complete")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Route all app.* loggers through uvicorn's handler
    _app_logger.setLevel(logging.INFO)
    for _h in logging.getLogger("uvicorn").handlers:
        if _h not in _app_logger.handlers:
            _app_logger.addHandler(_h)
    _app_logger.propagate = False

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await _auto_seed()

    from app import cache
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT DISTINCT countryiso3 FROM prices"))
        cache.wfp_countries = {row[0] for row in result.all()}
    logger.info("Cached %d WFP countries", len(cache.wfp_countries))

    async with mcp_http_app.lifespan(app):
        yield


def create_app() -> FastAPI:
    app = FastAPI(
        lifespan=lifespan,
        title="Global Food Price Monitor API",
        description="API for monitoring global food prices using WFP data",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", tags=["health"])
    async def health_check() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(auth_router_module.router, prefix="/api/v1")
    app.include_router(prices_router_module.router, prefix="/api/v1")
    app.include_router(analytics_router_module.router, prefix="/api/v1")
    app.include_router(reference_router_module.router, prefix="/api/v1")

    app.mount("/mcp", mcp_http_app)

    return app


app = create_app()
