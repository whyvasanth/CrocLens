from __future__ import annotations

import logging

from sqlalchemy import select

from app.core.config import settings
from app.core.logging import configure_logging
from app.db.session import SessionLocal
from app.models import User
from app.services.market_data_cache_service import capture_net_worth_snapshot

logger = logging.getLogger(__name__)


def run() -> dict[str, int]:
    totals = {"users": 0, "snapshots": 0}
    with SessionLocal() as db:
        users = list(db.scalars(select(User).order_by(User.created_at.asc())))
        for user in users:
            capture_net_worth_snapshot(db, user)
            totals["users"] += 1
            totals["snapshots"] += 1
        db.commit()
    logger.info("Net worth snapshot capture completed: %s", totals)
    return totals


def main() -> None:
    configure_logging(settings.log_level)
    run()


if __name__ == "__main__":
    main()
