from __future__ import annotations

import asyncio
import logging

from sqlalchemy import select

from app.core.config import settings
from app.core.logging import configure_logging
from app.db.session import SessionLocal
from app.models import Asset
from app.providers.registry import build_default_provider_registry
from app.services.market_data_cache_service import PUBLIC_MARKET_ASSET_TYPES, get_or_refresh_quote

logger = logging.getLogger(__name__)


async def run() -> dict[str, int]:
    registry = build_default_provider_registry()
    quote_providers = registry.providers_for("quote")
    if not quote_providers:
        logger.info("No configured quote providers are available.")
        return {"assets": 0, "refreshed": 0, "fresh_cache": 0, "stale_cache": 0, "unavailable": 0}

    provider = quote_providers[0]
    totals = {"assets": 0, "refreshed": 0, "fresh_cache": 0, "stale_cache": 0, "unavailable": 0}
    with SessionLocal() as db:
        assets = list(
            db.scalars(
                select(Asset)
                .where(Asset.asset_type.in_(PUBLIC_MARKET_ASSET_TYPES))
                .order_by(Asset.symbol.asc())
            )
        )
        for asset in assets:
            result = await get_or_refresh_quote(db, asset, provider)
            totals["assets"] += 1
            totals[result.status] += 1
        db.commit()
    logger.info("Market snapshot ingestion completed: %s", totals)
    return totals


def main() -> None:
    configure_logging(settings.log_level)
    asyncio.run(run())


if __name__ == "__main__":
    main()
