from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    action_plans,
    assistant,
    assets,
    auth,
    data_pipeline,
    evaluation,
    health,
    journal,
    market_news,
    onboarding,
    portfolio,
    retirement,
    security,
    tax,
    watchlist,
)
from app.core.config import settings
from app.core.logging import configure_logging
from app.core.middleware import SecurityHeadersAndRateLimitMiddleware


def create_app() -> FastAPI:
    configure_logging(settings.log_level)

    app = FastAPI(
        title="CrocLens API",
        description="REST API for the CrocLens beginner wealth intelligence platform.",
        version=settings.api_version,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(
        SecurityHeadersAndRateLimitMiddleware,
        rate_limit_per_minute=settings.rate_limit_per_minute,
    )

    app.include_router(health.router)
    app.include_router(portfolio.router, prefix=settings.api_prefix)
    app.include_router(assets.router, prefix=settings.api_prefix)
    app.include_router(auth.router, prefix=settings.api_prefix)
    app.include_router(onboarding.router, prefix=settings.api_prefix)
    app.include_router(action_plans.router, prefix=settings.api_prefix)
    app.include_router(assistant.router, prefix=settings.api_prefix)
    app.include_router(data_pipeline.router, prefix=settings.api_prefix)
    app.include_router(evaluation.router, prefix=settings.api_prefix)
    app.include_router(market_news.router, prefix=settings.api_prefix)
    app.include_router(tax.router, prefix=settings.api_prefix)
    app.include_router(retirement.router, prefix=settings.api_prefix)
    app.include_router(journal.router, prefix=settings.api_prefix)
    app.include_router(watchlist.router, prefix=settings.api_prefix)
    app.include_router(security.router, prefix=settings.api_prefix)

    return app


app = create_app()
