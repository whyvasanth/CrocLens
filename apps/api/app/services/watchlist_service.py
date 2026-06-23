from datetime import date
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Asset, User, WatchlistItem
from app.schemas.api import (
    DeleteRecordResponse,
    SourceMetadata,
    WatchlistCreateRequest,
    WatchlistItemResponse,
    WatchlistResponse,
    WatchlistUpdateRequest,
)
from app.services.mock_data import EDUCATIONAL_DISCLAIMER


WATCHLIST_SOURCE = SourceMetadata(
    name="CrocLens sample watchlist",
    freshness="Sample watchlist intelligence",
    as_of="2026-05-06",
)

PERSISTED_WATCHLIST_SOURCE = SourceMetadata(
    name="CrocLens watchlist records",
    freshness="Saved user watchlist",
    as_of=date.today().isoformat(),
)

ASSET_TYPE_MAP = {
    "stock": "Stocks",
    "etf": "ETFs",
    "crypto": "Crypto",
    "real_estate_market": "Real Estate",
    "bond": "Bonds",
    "treasury": "Treasuries",
    "other": "Other",
}


def get_watchlist(db: Session | None = None, user: User | None = None) -> WatchlistResponse:
    if db is None or user is None:
        return _sample_watchlist()

    items = list(
        db.scalars(
            select(WatchlistItem)
            .where(WatchlistItem.user_id == user.id)
            .order_by(WatchlistItem.created_at.asc())
        )
    )

    return WatchlistResponse(
        items=[_build_item_response(item, PERSISTED_WATCHLIST_SOURCE) for item in items],
        beginner_summary=(
            "Your watchlist is a research queue. It can help you track what to learn next without treating the list as a buy list."
        ),
        safe_research_prompts=[
            "Why am I watching this?",
            "What risk would make this unsuitable for my goal?",
            "What source would I check before making a real decision?",
        ],
        confidence="medium",
        data_limitations=[
            "Watchlist records are saved to your account.",
            "Latest price and provider freshness can be added from the market cache in a later slice.",
            "Educational summaries are deterministic and not financial advice.",
        ],
        sources=[PERSISTED_WATCHLIST_SOURCE],
        educational_disclaimer=EDUCATIONAL_DISCLAIMER,
    )


def create_watchlist_item(
    request: WatchlistCreateRequest,
    db: Session | None = None,
    user: User | None = None,
) -> WatchlistItemResponse:
    if db is None or user is None:
        return _preview_watchlist_item(request)

    asset = _get_or_create_asset(db, request)
    item = WatchlistItem(
        id=str(uuid4()),
        user_id=user.id,
        asset_id=asset.id,
        reason=request.why_watching.strip(),
        notes=None,
    )
    db.add(item)
    try:
        db.flush()
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This item is already on your watchlist.",
        ) from exc

    return _build_item_response(item, PERSISTED_WATCHLIST_SOURCE)


def update_watchlist_item(
    db: Session,
    user: User,
    item_id: str,
    request: WatchlistUpdateRequest,
) -> WatchlistItemResponse:
    item = _get_user_watchlist_item_or_404(db, user, item_id)
    if request.name is not None:
        item.asset.name = request.name.strip()
    if request.why_watching is not None:
        item.reason = request.why_watching.strip()
    if request.notes is not None:
        item.notes = request.notes.strip() or None

    db.add(item)
    db.flush()
    return _build_item_response(item, PERSISTED_WATCHLIST_SOURCE)


def delete_watchlist_item(db: Session, user: User, item_id: str) -> DeleteRecordResponse:
    item = _get_user_watchlist_item_or_404(db, user, item_id)
    db.delete(item)
    db.flush()
    return DeleteRecordResponse(status="deleted", id=item_id)


def _sample_watchlist() -> WatchlistResponse:
    items = [
        WatchlistItemResponse(
            id="watch_vti",
            symbol="VTI",
            name="Vanguard Total Stock Market ETF",
            asset_type="etf",
            why_watching="Researching a broad ETF as a simple diversified building block.",
            ai_summary="Broad-market ETFs can be beginner-friendly, but overlap, taxes, and time horizon still matter.",
            risk_notes=[
                "Still exposed to stock market downturns.",
                "ETF overlap can make diversification look stronger than it is.",
            ],
            opportunity_notes=[
                "May provide broad diversification in one fund.",
                "Can be easier to understand than many individual stocks.",
            ],
            source=WATCHLIST_SOURCE,
            confidence="medium",
            data_limitations=["Sample watchlist item only.", "No live fund data or holdings feed is connected."],
        ),
        WatchlistItemResponse(
            id="watch_us10y",
            symbol="US10Y",
            name="10Y Treasury yield",
            asset_type="treasury",
            why_watching="Learning how rates affect bonds, mortgages, cash, and stock valuations.",
            ai_summary="Treasury yields can influence several parts of a financial life, not only bonds.",
            risk_notes=[
                "Rate headlines can be noisy in the short term.",
                "Yield changes do not affect every asset in the same way.",
            ],
            opportunity_notes=[
                "Useful context for mortgage and bond decisions.",
                "Helps beginners compare cash yield with inflation.",
            ],
            source=WATCHLIST_SOURCE,
            confidence="medium",
            data_limitations=["Sample rate context only.", "No official Treasury API is connected yet."],
        ),
    ]

    return WatchlistResponse(
        items=items,
        beginner_summary="A watchlist is a research queue. It helps you track what to learn next without treating the list as a buy list.",
        safe_research_prompts=[
            "Why am I watching this?",
            "What risk would make this unsuitable for my goal?",
            "What source would I check before making a real decision?",
        ],
        confidence="medium",
        data_limitations=[
            "Uses sample watchlist entries only.",
            "No live prices, ratings, analyst data, or paid providers are connected.",
            "AI summaries are rule-based educational notes.",
        ],
        sources=[WATCHLIST_SOURCE],
        educational_disclaimer=EDUCATIONAL_DISCLAIMER,
    )


def _preview_watchlist_item(request: WatchlistCreateRequest) -> WatchlistItemResponse:
    symbol = request.symbol.upper()
    return WatchlistItemResponse(
        id=f"watch_preview_{symbol.lower()}",
        symbol=symbol,
        name=request.name,
        asset_type=request.asset_type,
        why_watching=request.why_watching,
        ai_summary=_summary_for(request.asset_type),
        risk_notes=_risk_notes_for(request.asset_type),
        opportunity_notes=_opportunity_notes_for(request.asset_type),
        source=WATCHLIST_SOURCE,
        confidence="medium",
        data_limitations=["Preview response only.", "Sign in to persist this watchlist item."],
    )


def _build_item_response(item: WatchlistItem, source: SourceMetadata) -> WatchlistItemResponse:
    asset_type = _watchlist_type_from_asset(item.asset.asset_type)
    return WatchlistItemResponse(
        id=item.id,
        symbol=item.asset.symbol,
        name=item.asset.name,
        asset_type=asset_type,
        why_watching=item.reason or "Research reason not entered yet.",
        ai_summary=_summary_for(asset_type),
        risk_notes=_risk_notes_for(asset_type),
        opportunity_notes=_opportunity_notes_for(asset_type),
        source=source,
        confidence="medium",
        data_limitations=[
            "Saved watchlist record.",
            "Latest price and external research summaries are not required for this educational note.",
        ],
    )


def _get_user_watchlist_item_or_404(db: Session, user: User, item_id: str) -> WatchlistItem:
    item = db.scalar(
        select(WatchlistItem)
        .where(WatchlistItem.id == item_id)
        .where(WatchlistItem.user_id == user.id)
    )
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Watchlist item was not found.")
    return item


def _get_or_create_asset(db: Session, request: WatchlistCreateRequest) -> Asset:
    symbol = request.symbol.strip().upper()
    asset_type = ASSET_TYPE_MAP[request.asset_type]
    asset = db.scalar(select(Asset).where(Asset.symbol == symbol).where(Asset.asset_type == asset_type))
    if asset is not None:
        if asset.name != request.name.strip():
            asset.name = request.name.strip()
            db.add(asset)
        return asset

    asset = Asset(
        id=str(uuid4()),
        symbol=symbol,
        name=request.name.strip(),
        asset_type=asset_type,
        currency="USD",
        data_source="watchlist_manual_entry",
    )
    db.add(asset)
    db.flush()
    return asset


def _watchlist_type_from_asset(asset_type: str) -> str:
    reverse = {value: key for key, value in ASSET_TYPE_MAP.items()}
    return reverse.get(asset_type, "other")


def _summary_for(asset_type: str) -> str:
    summaries = {
        "stock": "Individual stocks can teach company-specific risk, but concentration and volatility matter.",
        "etf": "ETFs can simplify broad exposure, but overlap, fees, taxes, and time horizon still matter.",
        "crypto": "Crypto can move sharply, so position size, security, taxes, and liquidity deserve extra review.",
        "real_estate_market": "Real estate markets are local and slower-moving; estimates should be treated as context, not exact values.",
        "bond": "Bond funds can add income and rate sensitivity, which behaves differently from stocks.",
        "treasury": "Treasury yields can influence cash, bonds, mortgage rates, and stock valuations.",
        "other": "A clear watch reason can help you research this item without treating the list as a recommendation.",
    }
    return summaries.get(asset_type, summaries["other"])


def _risk_notes_for(asset_type: str) -> list[str]:
    notes = {
        "stock": ["Single-company risk can be higher than broad funds.", "Price moves can be sharp around earnings or news."],
        "etf": ["ETF overlap can make diversification look stronger than it is.", "Funds can still fall during broad market downturns."],
        "crypto": ["Crypto prices can move sharply.", "Security, custody, and tax records can add complexity."],
        "real_estate_market": ["Local data may lag current selling prices.", "Property values are less liquid than public markets."],
        "bond": ["Bond prices can fall when rates rise.", "Credit and duration risk can vary by fund."],
        "treasury": ["Yield headlines can be noisy in the short term.", "Yield changes affect assets differently."],
        "other": ["The watchlist does not mean this item is appropriate.", "Review source quality before relying on metrics."],
    }
    return notes.get(asset_type, notes["other"])


def _opportunity_notes_for(asset_type: str) -> list[str]:
    notes = {
        "stock": ["Company research can help beginners understand business drivers."],
        "etf": ["May provide broad diversification in one fund."],
        "crypto": ["Can be useful for learning about high-volatility asset behavior."],
        "real_estate_market": ["Useful context for home equity and housing affordability."],
        "bond": ["Can help compare income, risk, and rate sensitivity."],
        "treasury": ["Useful context for cash yields, bond prices, and mortgage rates."],
        "other": ["A written watch reason can make research more focused."],
    }
    return notes.get(asset_type, notes["other"])
