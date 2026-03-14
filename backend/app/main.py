from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings


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

    # Routers will be included here in Phase 2+
    # from app.routers import prices, analytics, reference, auth
    # app.include_router(prices.router, prefix="/api/v1")
    # app.include_router(analytics.router, prefix="/api/v1")
    # app.include_router(reference.router, prefix="/api/v1")
    # app.include_router(auth.router, prefix="/api/v1")

    return app


app = create_app()
