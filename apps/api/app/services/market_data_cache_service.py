from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from typing import Literal
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    Asset,
    Holding,
    MarketPrice,
    Portfolio,
    PortfolioNetWorthSnapshot,
    ProviderError,
    ProviderIngestionRun,
    User,
)
from app.providers.base import BaseProvider
from app.providers.exceptions import ProviderError as ExternalProviderError
from app.providers.models import MarketHistory, MarketQuote, utc_now
from app.services.portfolio_service import get_or_create_default_portfolio, get_user_portfolio_summary

QuoteLookupStatus = Literal["fresh_cache", "refreshed", "stale_cache", "unavailable"]
PUBLIC_MARKET_ASSET_TYPES = {"Stocks", "ETFs", "Mutual Funds"}


@dataclass(frozen=True)
class QuoteLookupResult:
    status: QuoteLookupStatus
    price: MarketPrice | None
    warning: str | None = None


def get_latest_market_price(db: Session, asset_id: str, provider_name: str | None = None) -> MarketPrice | None:
    statement = select(MarketPrice).where(MarketPrice.asset_id == asset_id)
    if provider_name is not None:
        statement = statement.where(MarketPrice.source_name == provider_name)
    return db.scalar(statement.order_by(MarketPrice.data_as_of.desc(), MarketPrice.retrieved_at.desc()))


def is_market_price_fresh(market_price: MarketPrice, *, stale_after_seconds: int, now: datetime | None = None) -> bool:
    if market_price.is_stale:
        return False
    if market_price.retrieved_at is None:
        return False
    current_time = now or utc_now()
    return _as_utc(market_price.retrieved_at) >= current_time - timedelta(seconds=stale_after_seconds)


async def get_or_refresh_quote(
    db: Session,
    asset: Asset,
    provider: BaseProvider,
    *,
    now: datetime | None = None,
) -> QuoteLookupResult:
    existing = get_latest_market_price(db, asset.id, provider.name)
    if existing is not None and is_market_price_fresh(
        existing,
        stale_after_seconds=provider.config.stale_after_seconds,
        now=now,
    ):
        return QuoteLookupResult(status="fresh_cache", price=existing)

    run = start_provider_run(
        db,
        provider_name=provider.name,
        operation="quote_refresh",
        records_requested=1,
        metadata={"symbol": asset.symbol},
    )
    try:
        quote = await provider.get_quote(asset.symbol)
        market_price = upsert_quote_observation(db, asset, quote)
        complete_provider_run(db, run, status="completed", records_accepted=1)
        return QuoteLookupResult(status="refreshed", price=market_price)
    except Exception as exc:
        record_provider_error(
            db,
            provider_name=provider.name,
            operation="quote_refresh",
            asset_id=asset.id,
            symbol_or_series=asset.symbol,
            exc=exc,
        )
        complete_provider_run(
            db,
            run,
            status="failed",
            records_rejected=1,
            error_message=str(exc),
        )
        if existing is not None:
            existing.is_stale = True
            db.add(existing)
            return QuoteLookupResult(
                status="stale_cache",
                price=existing,
                warning="Provider refresh failed, so CrocLens returned the last stored observation and marked it stale.",
            )
        return QuoteLookupResult(
            status="unavailable",
            price=None,
            warning="Provider refresh failed and no stored observation exists.",
        )


def upsert_quote_observation(db: Session, asset: Asset, quote: MarketQuote) -> MarketPrice:
    if quote.price is None:
        raise ValueError("Cannot persist a market quote without a price.")

    data_as_of = quote.data_as_of or quote.retrieved_at
    price_date = data_as_of.date()
    existing = db.scalar(
        select(MarketPrice)
        .where(MarketPrice.asset_id == asset.id)
        .where(MarketPrice.price_date == price_date)
        .where(MarketPrice.source_name == quote.provider_name)
    )
    market_price = existing or MarketPrice(
        id=str(uuid4()),
        asset_id=asset.id,
        price_date=price_date,
        source_name=quote.provider_name,
    )
    market_price.close_price = quote.price
    market_price.currency = quote.currency or "USD"
    market_price.data_as_of = data_as_of
    market_price.retrieved_at = quote.retrieved_at
    market_price.provider_status = quote.provider_status
    market_price.data_quality = quote.data_quality
    market_price.is_stale = quote.is_stale
    market_price.is_sample_data = quote.is_sample_data
    market_price.source_url = quote.source_url
    market_price.data_limitations = quote.data_limitations
    market_price.raw_response_metadata = quote.raw_payload or {}
    db.add(market_price)
    db.flush()
    return market_price


def upsert_history_observations(db: Session, asset: Asset, history: MarketHistory) -> int:
    accepted = 0
    for point in history.points:
        quote = MarketQuote(
            provider_name=history.provider_name,
            provider_status=history.provider_status,
            symbol=history.symbol,
            asset_type=history.asset_type,
            price=point.close,
            currency=history.currency,
            data_as_of=point.observed_at,
            retrieved_at=history.retrieved_at,
            is_stale=history.is_stale,
            is_sample_data=history.is_sample_data,
            data_quality=history.data_quality,
            confidence=history.confidence,
            source_url=history.source_url,
            data_limitations=history.data_limitations,
        )
        upsert_quote_observation(db, asset, quote)
        accepted += 1
    return accepted


async def refresh_user_public_holding_prices(
    db: Session,
    user: User,
    provider: BaseProvider,
) -> dict[str, int]:
    counts = {"refreshed": 0, "fresh_cache": 0, "stale_cache": 0, "unavailable": 0, "skipped": 0}
    for holding in _load_user_public_holdings(db, user):
        if holding.quantity <= 0:
            counts["skipped"] += 1
            continue
        result = await get_or_refresh_quote(db, holding.asset, provider)
        counts[result.status] += 1
        if result.price is not None and result.status in {"refreshed", "fresh_cache", "stale_cache"}:
            holding.market_value = (holding.quantity * result.price.close_price).quantize(Decimal("0.01"))
            db.add(holding)
    db.flush()
    return counts


def capture_net_worth_snapshot(
    db: Session,
    user: User,
    *,
    snapshot_date: date | None = None,
) -> PortfolioNetWorthSnapshot:
    portfolio = get_or_create_default_portfolio(db, user)
    target_date = snapshot_date or datetime.now(tz=UTC).date()
    summary = get_user_portfolio_summary(db, user)
    existing = db.scalar(
        select(PortfolioNetWorthSnapshot)
        .where(PortfolioNetWorthSnapshot.portfolio_id == portfolio.id)
        .where(PortfolioNetWorthSnapshot.snapshot_date == target_date)
    )
    snapshot = existing or PortfolioNetWorthSnapshot(
        id=str(uuid4()),
        portfolio_id=portfolio.id,
        user_id=user.id,
        snapshot_date=target_date,
    )
    snapshot.total_assets = Decimal(str(summary.total_assets)).quantize(Decimal("0.01"))
    snapshot.total_liabilities = Decimal(str(summary.total_liabilities)).quantize(Decimal("0.01"))
    snapshot.net_worth = Decimal(str(summary.net_worth)).quantize(Decimal("0.01"))
    snapshot.source_name = "CrocLens portfolio records"
    snapshot.data_quality = "manual"
    db.add(snapshot)
    db.flush()
    return snapshot


def start_provider_run(
    db: Session,
    *,
    provider_name: str,
    operation: str,
    records_requested: int = 0,
    metadata: dict | None = None,
) -> ProviderIngestionRun:
    run = ProviderIngestionRun(
        id=str(uuid4()),
        provider_name=provider_name,
        operation=operation,
        status="running",
        started_at=utc_now(),
        records_requested=records_requested,
        records_accepted=0,
        records_rejected=0,
        metadata_json=metadata or {},
    )
    db.add(run)
    db.flush()
    return run


def complete_provider_run(
    db: Session,
    run: ProviderIngestionRun,
    *,
    status: str,
    records_accepted: int = 0,
    records_rejected: int = 0,
    error_message: str | None = None,
) -> ProviderIngestionRun:
    run.status = status
    run.completed_at = utc_now()
    run.records_accepted = records_accepted
    run.records_rejected = records_rejected
    run.error_message = error_message
    db.add(run)
    db.flush()
    return run


def record_provider_error(
    db: Session,
    *,
    provider_name: str,
    operation: str,
    asset_id: str | None,
    symbol_or_series: str | None,
    exc: Exception,
) -> ProviderError:
    retryable = True
    error_code = "provider_unavailable"
    if isinstance(exc, ExternalProviderError):
        error_code = exc.code
        retryable = error_code not in {"provider_invalid_symbol", "provider_capability_not_supported"}
    provider_error = ProviderError(
        id=str(uuid4()),
        provider_name=provider_name,
        operation=operation,
        asset_id=asset_id,
        symbol_or_series=symbol_or_series,
        error_code=error_code,
        error_message=str(exc),
        retryable=retryable,
    )
    db.add(provider_error)
    db.flush()
    return provider_error


def _load_user_public_holdings(db: Session, user: User) -> list[Holding]:
    return list(
        db.scalars(
            select(Holding)
            .join(Holding.portfolio)
            .where(Portfolio.user_id == user.id)
            .join(Holding.asset)
            .where(Asset.asset_type.in_(PUBLIC_MARKET_ASSET_TYPES))
            .order_by(Holding.created_at.asc())
        )
    )


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)
