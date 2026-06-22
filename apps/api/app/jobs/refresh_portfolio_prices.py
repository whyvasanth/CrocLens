from __future__ import annotations

import asyncio
import logging

from sqlalchemy import select

from app.core.config import settings
from app.core.logging import configure_logging
from app.db.session import SessionLocal
from app.models import User
from app.providers.registry import build_default_provider_registry
from app.services.market_data_cache_service import refresh_user_public_holding_prices

logger = logging.getLogger(__name__)


async def run() -> dict[str, int]:
    registry = build_default_provider_registry()
    quote_providers = registry.providers_for("quote")
    if not quote_providers:
        logger.info("No configured quote providers are available.")
        return {"users": 0, "refreshed": 0, "fresh_cache": 0, "stale_cache": 0, "unavailable": 0, "skipped": 0}

    provider = quote_providers[0]
    totals = {"users": 0, "refreshed": 0, "fresh_cache": 0, "stale_cache": 0, "unavailable": 0, "skipped": 0}
    with SessionLocal() as db:
        users = list(db.scalars(select(User).order_by(User.created_at.asc())))
        for user in users:
            counts = await refresh_user_public_holding_prices(db, user, provider)
            totals["users"] += 1
            for key, value in counts.items():
                totals[key] += value
        db.commit()
    logger.info("Portfolio price refresh completed: %s", totals)
    return totals


def main() -> None:
    configure_logging(settings.log_level)
    asyncio.run(run())


if __name__ == "__main__":
    main()
