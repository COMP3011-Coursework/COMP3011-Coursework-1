from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.mcp.tools import mcp as mcp_server
from app.routers import analytics as analytics_router_module
from app.routers import auth as auth_router_module
from app.routers import prices as prices_router_module
from app.routers import reference as reference_router_module


def create_app() -> FastAPI:
    app = FastAPI(
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

    app.mount("/mcp", mcp_server.http_app())

    return app


app = create_app()
