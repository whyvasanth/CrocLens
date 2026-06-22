from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
import re
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Asset, Holding, MarketPrice, Portfolio, PortfolioNetWorthSnapshot, User
from app.providers.base import BaseProvider
from app.providers.exceptions import ProviderError as ExternalProviderError
from app.providers.models import MarketHistory, utc_now
from app.providers.registry import ProviderRegistry
from app.schemas.api import (
    MarketHistoryPointResponse,
    MarketHistoryResponse,
    MarketInterval,
    MarketPeriod,
    MarketQuoteResponse,
    MarketSnapshotItemResponse,
    MarketSnapshotResponse,
    PortfolioHistoryPointResponse,
    PortfolioHistoryResponse,
    PortfolioRefreshPricesResponse,
)
from app.services.data_pipeline import get_latest_market_observations
from app.services.market_data_cache_service import (
    PUBLIC_MARKET_ASSET_TYPES,
    capture_net_worth_snapshot,
    complete_provider_run,
    get_latest_market_price,
    get_or_refresh_quote,
    is_market_price_fresh,
    record_provider_error,
    refresh_user_public_holding_prices,
    start_provider_run,
    upsert_history_observations,
)
from app.services.mock_data import EDUCATIONAL_DISCLAIMER
from app.services.portfolio_service import get_user_portfolio_summary

SYMBOL_PATTERN = re.compile(r"^[A-Z0-9^][A-Z0-9.\-=^]{0,19}$")
SUPPORTED_PERIODS: set[str] = {"1M", "3M", "6M", "YTD", "1Y", "5Y", "ALL"}
SUPPORTED_INTERVALS: set[str] = {"1d", "1wk", "1mo"}


def normalize_market_symbol(symbol: str) -> str:
    normalized = symbol.strip().upper()
    if not SYMBOL_PATTERN.match(normalized):
        raise HTTPException(
            status_code=422,
            detail="Symbol must be 1-20 characters and contain only ticker-safe characters.",
        )
    return normalized


def validate_period(period: str) -> MarketPeriod:
    normalized = period.strip().upper()
    if normalized not in SUPPORTED_PERIODS:
        raise HTTPException(
            status_code=422,
            detail="Period must be one of 1M, 3M, 6M, YTD, 1Y, 5Y, or ALL.",
        )
    return normalized  # type: ignore[return-value]


def validate_interval(interval: str) -> MarketInterval:
    normalized = interval.strip().lower()
    if normalized not in SUPPORTED_INTERVALS:
        raise HTTPException(
            status_code=422,
            detail="Interval must be one of 1d, 1wk, or 1mo.",
        )
    return normalized  # type: ignore[return-value]


async def get_market_quote_response(
    db: Session,
    registry: ProviderRegistry,
    symbol: str,
) -> MarketQuoteResponse:
    normalized_symbol = normalize_market_symbol(symbol)
    provider = _first_provider_or_none(registry, "quote")
    asset = _get_or_create_public_asset(db, normalized_symbol)
    if provider is None:
        return _unavailable_quote_response(normalized_symbol, "No configured quote provider is available.")

    result = await get_or_refresh_quote(db, asset, provider)
    if result.price is None:
        return _unavailable_quote_response(normalized_symbol, result.warning or "Quote is unavailable.")

    return _market_price_to_quote_response(
        asset=asset,
        price=result.price,
        warning=result.warning,
    )


async def get_market_history_response(
    db: Session,
    registry: ProviderRegistry,
    symbol: str,
    period: str,
    interval: str,
) -> MarketHistoryResponse:
    normalized_symbol = normalize_market_symbol(symbol)
    normalized_period = validate_period(period)
    normalized_interval = validate_interval(interval)
    provider = _first_provider_or_none(registry, "history")
    asset = _get_or_create_public_asset(db, normalized_symbol)
    if provider is None:
        return _empty_history_response(
            asset=asset,
            period=normalized_period,
            interval=normalized_interval,
            warning="No configured history provider is available.",
        )

    stored_points = _stored_history_points(db, asset.id, provider.name, normalized_period)
    latest_stored = stored_points[-1] if stored_points else None
    if latest_stored is not None and is_market_price_fresh(
        latest_stored,
        stale_after_seconds=provider.config.stale_after_seconds,
    ):
        return _stored_points_to_history_response(
            asset=asset,
            points=stored_points,
            period=normalized_period,
            interval=normalized_interval,
            warning=None,
        )

    run = start_provider_run(
        db,
        provider_name=provider.name,
        operation="history_refresh",
        records_requested=1,
        metadata={"symbol": asset.symbol, "period": normalized_period, "interval": normalized_interval},
    )
    try:
        history = await provider.get_history(asset.symbol, normalized_period, normalized_interval)
        accepted = upsert_history_observations(db, asset, history)
        complete_provider_run(db, run, status="completed", records_accepted=accepted)
        refreshed_points = _stored_history_points(db, asset.id, provider.name, normalized_period)
        return _stored_points_to_history_response(
            asset=asset,
            points=refreshed_points,
            period=normalized_period,
            interval=normalized_interval,
            warning=None,
        )
    except Exception as exc:
        record_provider_error(
            db,
            provider_name=provider.name,
            operation="history_refresh",
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
        if stored_points:
            for point in stored_points:
                point.is_stale = True
                db.add(point)
            return _stored_points_to_history_response(
                asset=asset,
                points=stored_points,
                period=normalized_period,
                interval=normalized_interval,
                warning="Provider history refresh failed, so CrocLens returned stored stale observations.",
            )
        return _empty_history_response(
            asset=asset,
            period=normalized_period,
            interval=normalized_interval,
            warning="Provider history refresh failed and no stored history exists.",
        )


def get_market_snapshot_response() -> MarketSnapshotResponse:
    items = []
    for record in get_latest_market_observations():
        items.append(
            MarketSnapshotItemResponse(
                symbol=record.symbol,
                name=record.name,
                asset_class=record.asset_class,
                metric_type=record.metric_type,
                value=record.value,
                unit=record.unit,
                currency=record.currency,
                change_percent=record.change_percent,
                provider_status="sample",
                source_name=record.source.name,
                source_url=record.source_url,
                data_as_of=record.as_of,
                retrieved_at=record.retrieved_at,
                is_stale=False,
                is_sample_data=True,
                data_quality="sample",
                confidence="medium",
                data_limitations=record.data_limitations,
                warning="Demo market snapshot uses sample data, not live provider data.",
            )
        )
    return MarketSnapshotResponse(
        items=items,
        provider_status="sample",
        is_sample_data=True,
        data_quality="sample",
        data_limitations=[
            "This endpoint currently returns the deterministic sample market snapshot.",
            "Live provider observations are exposed through quote/history endpoints and will be wired into dashboard UI later.",
        ],
        educational_disclaimer=EDUCATIONAL_DISCLAIMER,
    )


async def refresh_portfolio_prices_response(
    db: Session,
    registry: ProviderRegistry,
    user: User,
) -> PortfolioRefreshPricesResponse:
    provider = _first_provider_or_none(registry, "quote")
    warnings: list[str] = []
    if provider is None:
        counts = {"refreshed": 0, "fresh_cache": 0, "stale_cache": 0, "unavailable": 0, "skipped": 0}
        warnings.append("No configured quote provider is available, so public holdings were not provider-valued.")
    else:
        counts = await refresh_user_public_holding_prices(db, user, provider)

    valuation_counts = _portfolio_valuation_counts(db, user)
    snapshot = capture_net_worth_snapshot(db, user)
    summary = get_user_portfolio_summary(db, user)
    if counts.get("stale_cache", 0):
        warnings.append("Some holdings used stale stored prices because provider refresh failed.")
    if counts.get("unavailable", 0):
        warnings.append("Some holdings could not be provider-valued because no quote was available.")
    return PortfolioRefreshPricesResponse(
        status="completed_with_warnings" if warnings else "completed",
        provider_name=provider.name if provider is not None else None,
        counts=counts,
        valuation_counts=valuation_counts,
        snapshot=_snapshot_to_response(snapshot),
        summary=summary,
        warnings=warnings,
        confidence="medium",
        data_limitations=[
            "Only stock, ETF, and mutual fund holdings with quantity are eligible for provider valuation in this slice.",
            "Manual values for cash, real estate, retirement, crypto, and unsupported assets are preserved.",
            "CrocLens does not convert currencies yet.",
        ],
        educational_disclaimer=EDUCATIONAL_DISCLAIMER,
    )


def get_portfolio_history_response(db: Session, user: User) -> PortfolioHistoryResponse:
    snapshots = list(
        db.scalars(
            select(PortfolioNetWorthSnapshot)
            .where(PortfolioNetWorthSnapshot.user_id == user.id)
            .order_by(PortfolioNetWorthSnapshot.snapshot_date.asc())
        )
    )
    return PortfolioHistoryResponse(
        points=[_snapshot_to_response(snapshot) for snapshot in snapshots],
        confidence="medium" if snapshots else "low",
        data_limitations=[
            "Portfolio history uses stored snapshots only; CrocLens does not invent trend lines.",
            "Run a portfolio refresh or snapshot job to create new history points.",
        ],
        educational_disclaimer=EDUCATIONAL_DISCLAIMER,
    )


def _first_provider_or_none(registry: ProviderRegistry, capability: str) -> BaseProvider | None:
    providers = registry.providers_for(capability)  # type: ignore[arg-type]
    return providers[0] if providers else None


def _get_or_create_public_asset(db: Session, symbol: str) -> Asset:
    existing = db.scalar(
        select(Asset)
        .where(Asset.symbol == symbol)
        .where(Asset.asset_type.in_(PUBLIC_MARKET_ASSET_TYPES))
        .order_by(Asset.created_at.asc())
    )
    if existing is not None:
        return existing

    asset = Asset(
        id=str(uuid4()),
        symbol=symbol,
        name=symbol,
        asset_type="Stocks",
        currency="USD",
        data_source="market_endpoint",
    )
    db.add(asset)
    db.flush()
    return asset


def _market_price_to_quote_response(asset: Asset, price: MarketPrice, warning: str | None) -> MarketQuoteResponse:
    return MarketQuoteResponse(
        symbol=asset.symbol,
        name=asset.name,
        asset_type=asset.asset_type,
        price=_float_or_none(price.close_price),
        currency=price.currency,
        provider_status=price.provider_status,
        source_name=price.source_name,
        source_url=price.source_url,
        data_as_of=price.data_as_of,
        retrieved_at=price.retrieved_at,
        is_stale=price.is_stale,
        is_sample_data=price.is_sample_data,
        data_quality=price.data_quality,
        confidence="medium",
        data_limitations=list(price.data_limitations or []),
        warning=warning,
    )


def _unavailable_quote_response(symbol: str, warning: str) -> MarketQuoteResponse:
    now = utc_now()
    return MarketQuoteResponse(
        symbol=symbol,
        name=symbol,
        asset_type="unknown",
        price=None,
        currency="USD",
        provider_status="unavailable",
        source_name="none",
        source_url=None,
        data_as_of=None,
        retrieved_at=now,
        is_stale=True,
        is_sample_data=False,
        data_quality="unavailable",
        confidence="low",
        data_limitations=["No market price was returned. CrocLens did not substitute sample data."],
        warning=warning,
    )


def _stored_history_points(db: Session, asset_id: str, provider_name: str, period: MarketPeriod) -> list[MarketPrice]:
    statement = (
        select(MarketPrice)
        .where(MarketPrice.asset_id == asset_id)
        .where(MarketPrice.source_name == provider_name)
        .order_by(MarketPrice.data_as_of.asc())
    )
    start_date = _period_start_date(period)
    if start_date is not None:
        statement = statement.where(MarketPrice.price_date >= start_date)
    return list(db.scalars(statement))


def _stored_points_to_history_response(
    *,
    asset: Asset,
    points: list[MarketPrice],
    period: MarketPeriod,
    interval: MarketInterval,
    warning: str | None,
) -> MarketHistoryResponse:
    latest = points[-1] if points else None
    if latest is None:
        return _empty_history_response(asset=asset, period=period, interval=interval, warning=warning)
    return MarketHistoryResponse(
        symbol=asset.symbol,
        name=asset.name,
        asset_type=asset.asset_type,
        period=period,
        interval=interval,
        currency=latest.currency,
        points=[
            MarketHistoryPointResponse(
                observed_at=point.data_as_of or datetime.combine(point.price_date, datetime.min.time(), tzinfo=UTC),
                close=float(point.close_price),
                source_name=point.source_name,
                data_quality=point.data_quality,
                is_stale=point.is_stale,
            )
            for point in points
        ],
        provider_status=latest.provider_status,
        source_name=latest.source_name,
        source_url=latest.source_url,
        data_as_of=latest.data_as_of,
        retrieved_at=latest.retrieved_at,
        is_stale=any(point.is_stale for point in points),
        is_sample_data=any(point.is_sample_data for point in points),
        data_quality="stale" if any(point.is_stale for point in points) else latest.data_quality,
        confidence="medium",
        data_limitations=list(latest.data_limitations or []),
        warning=warning,
    )


def _empty_history_response(
    *,
    asset: Asset,
    period: MarketPeriod,
    interval: MarketInterval,
    warning: str | None,
) -> MarketHistoryResponse:
    return MarketHistoryResponse(
        symbol=asset.symbol,
        name=asset.name,
        asset_type=asset.asset_type,
        period=period,
        interval=interval,
        currency=asset.currency,
        points=[],
        provider_status="unavailable",
        source_name="none",
        source_url=None,
        data_as_of=None,
        retrieved_at=utc_now(),
        is_stale=True,
        is_sample_data=False,
        data_quality="unavailable",
        confidence="low",
        data_limitations=["No market history was returned. CrocLens did not substitute sample history."],
        warning=warning,
    )


def _period_start_date(period: MarketPeriod) -> date | None:
    today = datetime.now(tz=UTC).date()
    if period == "1M":
        return today - timedelta(days=31)
    if period == "3M":
        return today - timedelta(days=93)
    if period == "6M":
        return today - timedelta(days=186)
    if period == "YTD":
        return date(today.year, 1, 1)
    if period == "1Y":
        return today - timedelta(days=366)
    if period == "5Y":
        return today - timedelta(days=366 * 5)
    return None


def _portfolio_valuation_counts(db: Session, user: User) -> dict[str, int]:
    counts = {
        "provider_valued": 0,
        "manually_valued": 0,
        "stale_value": 0,
        "unavailable_value": 0,
    }
    holdings = list(
        db.scalars(
            select(Holding)
            .join(Holding.portfolio)
            .where(Portfolio.user_id == user.id)
            .join(Holding.asset)
            .order_by(Holding.created_at.asc())
        )
    )
    for holding in holdings:
        if holding.asset.asset_type not in PUBLIC_MARKET_ASSET_TYPES or holding.quantity <= 0:
            counts["manually_valued"] += 1
            continue
        latest_price = get_latest_market_price(db, holding.asset_id)
        if latest_price is None:
            counts["unavailable_value"] += 1
        elif latest_price.is_stale:
            counts["stale_value"] += 1
        else:
            counts["provider_valued"] += 1
    return counts


def _snapshot_to_response(snapshot: PortfolioNetWorthSnapshot) -> PortfolioHistoryPointResponse:
    return PortfolioHistoryPointResponse(
        snapshot_date=snapshot.snapshot_date.isoformat(),
        total_assets=float(snapshot.total_assets),
        total_liabilities=float(snapshot.total_liabilities),
        net_worth=float(snapshot.net_worth),
        source_name=snapshot.source_name,
        data_quality=snapshot.data_quality,
    )


def _float_or_none(value: Decimal | None) -> float | None:
    return None if value is None else float(value)
