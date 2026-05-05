from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import action_plans, assistant, assets, health, portfolio
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title="CrocLens API",
        description="Mock REST API for the CrocLens beginner wealth intelligence platform.",
        version=settings.api_version,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(portfolio.router, prefix=settings.api_prefix)
    app.include_router(assets.router, prefix=settings.api_prefix)
    app.include_router(action_plans.router, prefix=settings.api_prefix)
    app.include_router(assistant.router, prefix=settings.api_prefix)

    return app


app = create_app()

