from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ActionPlan, DecisionJournalEntry, Holding, Portfolio, RetirementAccount, TaxLot, User, WatchlistItem
from app.schemas.api import AssistantEvidenceItem, SourceMetadata
from app.services.market_data_cache_service import get_latest_market_price
from app.services.mock_data import MOCK_SOURCE, get_portfolio_summary
from app.services.portfolio_service import get_user_portfolio_summary, list_user_holdings, list_user_liabilities


CROC_GUIDE_CONTEXT_SOURCE = SourceMetadata(
    name="CrocLens grounded context",
    freshness="Saved user records at request time",
    as_of=date.today().isoformat(),
)


@dataclass(frozen=True)
class GroundedGuideContext:
    user_name: str
    is_authenticated: bool
    total_assets: float
    total_liabilities: float
    net_worth: float
    debt_to_asset_percent: float
    holdings_count: int
    liabilities_count: int
    allocation_labels: list[str]
    top_holding_label: str | None
    top_liability_label: str | None
    risk_score: int | None
    diversification_score: int | None
    profile_goal: str | None
    risk_tolerance: str | None
    time_horizon: str | None
    watchlist_count: int
    journal_open_count: int
    journal_reviewed_count: int
    action_plan_open_count: int
    action_plan_completed_count: int
    retirement_accounts_count: int
    retirement_balance: float
    tax_lot_count: int
    unrealized_tax_loss: float
    evidence: list[AssistantEvidenceItem]
    sources: list[SourceMetadata]
    data_limitations: list[str]
    data_as_of: str | None
    retrieved_at: str | None
    is_sample_data: bool
    data_quality: str
    provider_status: str
    is_stale: bool

    @property
    def label(self) -> str:
        return "your saved CrocLens records" if self.is_authenticated else "clearly labeled CrocLens demo data"


def build_grounded_guide_context(db: Session | None = None, user: User | None = None) -> GroundedGuideContext:
    if db is None or user is None:
        return _sample_context()
    return _authenticated_context(db, user)


def context_summary(context: GroundedGuideContext) -> str:
    return (
        f"{context.user_name} has net worth ${context.net_worth:,.0f}, "
        f"assets ${context.total_assets:,.0f}, liabilities ${context.total_liabilities:,.0f}, "
        f"debt-to-asset ratio {context.debt_to_asset_percent:.1f}%, "
        f"{context.holdings_count} holdings, {context.liabilities_count} liabilities, "
        f"{context.watchlist_count} watchlist items, {context.journal_open_count} open journal entries, "
        f"and {context.action_plan_open_count} open action items. Context source: {context.label}."
    )


def _authenticated_context(db: Session, user: User) -> GroundedGuideContext:
    now = datetime.now(tz=UTC)
    portfolio = get_user_portfolio_summary(db, user)
    holdings = list_user_holdings(db, user)
    liabilities = list_user_liabilities(db, user)
    watchlist_items = _load_watchlist_items(db, user)
    journal_entries = _load_journal_entries(db, user)
    action_plans = _load_action_plans(db, user)
    retirement_accounts = _load_retirement_accounts(db, user)
    tax_lots = _load_tax_lots(db, user)
    market_metadata = _market_metadata_for_holdings(db, holdings)

    risk_score = _score_value(portfolio.scores, "Risk")
    diversification_score = _score_value(portfolio.scores, "Diversification")
    top_holding = max(holdings, key=lambda item: item.market_value, default=None)
    top_liability = max(liabilities, key=lambda item: item.balance, default=None)
    retirement_balance = sum(_to_float(account.balance) for account in retirement_accounts)
    tax_loss = _estimate_tax_loss(tax_lots)
    allocation_labels = [f"{item.asset_class} {item.percent:.1f}%" for item in portfolio.allocation[:4]]

    profile = user.profile
    data_quality = _data_quality(holdings, market_metadata["has_provider_data"], market_metadata["is_stale"])
    provider_status = _provider_status(market_metadata["provider_status"], market_metadata["has_provider_data"])
    data_as_of = market_metadata["data_as_of"] or date.today().isoformat()
    retrieved_at = market_metadata["retrieved_at"] or now.isoformat()
    is_stale = bool(market_metadata["is_stale"])

    limitations = [
        "Uses only records saved in this CrocLens account.",
        "Manual values are not independently verified.",
        "Provider prices may be delayed, cached, stale, or unavailable.",
        "CrocLens does not convert currencies yet.",
    ]
    if not holdings:
        limitations.insert(0, "No holdings are saved yet, so portfolio observations are limited.")
    if not liabilities:
        limitations.append("No liabilities are saved yet, so debt observations may be incomplete.")
    if not market_metadata["has_provider_data"]:
        limitations.append("No stored provider price was found for the current holdings.")

    sources = _dedupe_sources([CROC_GUIDE_CONTEXT_SOURCE, *portfolio.sources, *market_metadata["sources"]])
    evidence = [
        _evidence("Net worth", f"${portfolio.net_worth:,.0f}", "CrocLens portfolio records", data_as_of, retrieved_at, False, data_quality, provider_status, is_stale, limitations[:2]),
        _evidence("Assets tracked", f"${portfolio.total_assets:,.0f} across {len(portfolio.allocation)} asset groups", "CrocLens portfolio records", data_as_of, retrieved_at, False, data_quality, provider_status, is_stale),
        _evidence("Liabilities tracked", f"${portfolio.total_liabilities:,.0f}", "CrocLens liability records", data_as_of, retrieved_at, False, data_quality, provider_status, is_stale),
        _evidence("Watchlist", f"{len(watchlist_items)} saved research items", "CrocLens watchlist records", data_as_of, retrieved_at, False, "user_entered", "manual", False),
        _evidence("Decision journal", f"{_status_count(journal_entries, 'open')} open, {_status_count(journal_entries, 'reviewed')} reviewed", "CrocLens decision journal records", data_as_of, retrieved_at, False, "user_entered", "manual", False),
        _evidence("Action plans", f"{_open_action_count(action_plans)} open, {_completed_action_count(action_plans)} completed", "CrocLens action plan records", data_as_of, retrieved_at, False, "user_entered", "manual", False),
        _evidence("Retirement", f"${retirement_balance:,.0f} across {len(retirement_accounts)} accounts", "CrocLens retirement records", data_as_of, retrieved_at, False, "user_entered", "manual", False),
        _evidence("Tax lots", f"{len(tax_lots)} lots; ${tax_loss:,.0f} estimated unrealized losses", "CrocLens tax lot records", data_as_of, retrieved_at, False, "user_entered", "manual", False),
    ]

    if market_metadata["has_provider_data"]:
        evidence.append(
            _evidence(
                "Market freshness",
                market_metadata["market_summary"],
                market_metadata["source_name"] or "Stored provider observations",
                data_as_of,
                retrieved_at,
                False,
                market_metadata["data_quality"] or "provider_observation",
                provider_status,
                is_stale,
                market_metadata["limitations"],
            )
        )

    return GroundedGuideContext(
        user_name=portfolio.user_name,
        is_authenticated=True,
        total_assets=portfolio.total_assets,
        total_liabilities=portfolio.total_liabilities,
        net_worth=portfolio.net_worth,
        debt_to_asset_percent=portfolio.debt_impact.debt_to_asset_percent,
        holdings_count=len(holdings),
        liabilities_count=len(liabilities),
        allocation_labels=allocation_labels,
        top_holding_label=_holding_label(top_holding),
        top_liability_label=_liability_label(top_liability),
        risk_score=risk_score,
        diversification_score=diversification_score,
        profile_goal=profile.primary_goal if profile is not None else None,
        risk_tolerance=profile.risk_tolerance if profile is not None else None,
        time_horizon=profile.time_horizon if profile is not None else None,
        watchlist_count=len(watchlist_items),
        journal_open_count=_status_count(journal_entries, "open"),
        journal_reviewed_count=_status_count(journal_entries, "reviewed"),
        action_plan_open_count=_open_action_count(action_plans),
        action_plan_completed_count=_completed_action_count(action_plans),
        retirement_accounts_count=len(retirement_accounts),
        retirement_balance=retirement_balance,
        tax_lot_count=len(tax_lots),
        unrealized_tax_loss=tax_loss,
        evidence=evidence,
        sources=sources,
        data_limitations=limitations,
        data_as_of=data_as_of,
        retrieved_at=retrieved_at,
        is_sample_data=False,
        data_quality=data_quality,
        provider_status=provider_status,
        is_stale=is_stale,
    )


def _sample_context() -> GroundedGuideContext:
    now = datetime.now(tz=UTC)
    portfolio = get_portfolio_summary()
    allocation_labels = [f"{item.asset_class} {item.percent:.1f}%" for item in portfolio.allocation[:4]]
    limitations = [
        "This response uses CrocLens demo data, not a saved user account.",
        "No live account aggregation, tax filing context, or personalized provider feed is connected in demo mode.",
    ]
    evidence = [
        _evidence("Demo net worth", f"${portfolio.net_worth:,.0f}", MOCK_SOURCE.name, MOCK_SOURCE.as_of, now.isoformat(), True, "sample", "sample", False, limitations),
        _evidence("Demo allocation", ", ".join(allocation_labels), MOCK_SOURCE.name, MOCK_SOURCE.as_of, now.isoformat(), True, "sample", "sample", False),
        _evidence("Demo debt impact", f"{portfolio.debt_impact.debt_to_asset_percent:.1f}% debt-to-asset ratio", MOCK_SOURCE.name, MOCK_SOURCE.as_of, now.isoformat(), True, "sample", "sample", False),
    ]
    return GroundedGuideContext(
        user_name=portfolio.user_name,
        is_authenticated=False,
        total_assets=portfolio.total_assets,
        total_liabilities=portfolio.total_liabilities,
        net_worth=portfolio.net_worth,
        debt_to_asset_percent=portfolio.debt_impact.debt_to_asset_percent,
        holdings_count=len(portfolio.allocation),
        liabilities_count=1 if portfolio.total_liabilities > 0 else 0,
        allocation_labels=allocation_labels,
        top_holding_label=allocation_labels[0] if allocation_labels else None,
        top_liability_label="Sample mortgage and education debt",
        risk_score=_score_value(portfolio.scores, "Risk"),
        diversification_score=_score_value(portfolio.scores, "Diversification"),
        profile_goal=None,
        risk_tolerance=None,
        time_horizon=None,
        watchlist_count=2,
        journal_open_count=2,
        journal_reviewed_count=0,
        action_plan_open_count=len(portfolio.scores[:2]),
        action_plan_completed_count=0,
        retirement_accounts_count=1,
        retirement_balance=87_000,
        tax_lot_count=3,
        unrealized_tax_loss=2_005,
        evidence=evidence,
        sources=[MOCK_SOURCE],
        data_limitations=limitations,
        data_as_of=MOCK_SOURCE.as_of,
        retrieved_at=now.isoformat(),
        is_sample_data=True,
        data_quality="sample",
        provider_status="sample",
        is_stale=False,
    )


def _load_watchlist_items(db: Session, user: User) -> list[WatchlistItem]:
    return list(db.scalars(select(WatchlistItem).where(WatchlistItem.user_id == user.id)))


def _load_journal_entries(db: Session, user: User) -> list[DecisionJournalEntry]:
    return list(db.scalars(select(DecisionJournalEntry).where(DecisionJournalEntry.user_id == user.id)))


def _load_action_plans(db: Session, user: User) -> list[ActionPlan]:
    return list(db.scalars(select(ActionPlan).where(ActionPlan.user_id == user.id)))


def _load_retirement_accounts(db: Session, user: User) -> list[RetirementAccount]:
    return list(db.scalars(select(RetirementAccount).where(RetirementAccount.user_id == user.id)))


def _load_tax_lots(db: Session, user: User) -> list[TaxLot]:
    return list(
        db.scalars(
            select(TaxLot)
            .join(Holding, TaxLot.holding_id == Holding.id)
            .join(Portfolio, Holding.portfolio_id == Portfolio.id)
            .where(Portfolio.user_id == user.id)
        )
    )


def _market_metadata_for_holdings(db: Session, holdings: list) -> dict:
    latest_prices = []
    for holding in holdings:
        price = get_latest_market_price(db, holding.asset_id)
        if price is not None:
            latest_prices.append(price)

    if not latest_prices:
        return {
            "has_provider_data": False,
            "is_stale": False,
            "provider_status": None,
            "data_quality": None,
            "data_as_of": None,
            "retrieved_at": None,
            "source_name": None,
            "market_summary": "No stored provider observations found.",
            "sources": [],
            "limitations": ["No stored provider observation was found for the current holdings."],
        }

    latest = max(latest_prices, key=lambda item: _safe_datetime(item.data_as_of or item.retrieved_at))
    stale_count = sum(1 for item in latest_prices if item.is_stale)
    source_names = sorted({item.source_name for item in latest_prices})
    limitations = []
    for item in latest_prices:
        limitations.extend(list(item.data_limitations or []))
    return {
        "has_provider_data": True,
        "is_stale": stale_count > 0,
        "provider_status": "stale" if stale_count else latest.provider_status,
        "data_quality": "stale" if stale_count else latest.data_quality,
        "data_as_of": _dt_or_date_iso(latest.data_as_of),
        "retrieved_at": _dt_or_date_iso(latest.retrieved_at),
        "source_name": ", ".join(source_names),
        "market_summary": f"{len(latest_prices)} stored price observations from {', '.join(source_names)}; {stale_count} stale.",
        "sources": [
            SourceMetadata(
                name=item.source_name,
                freshness="Latest stored provider observation",
                as_of=_dt_or_date_iso(item.data_as_of),
            )
            for item in latest_prices
        ],
        "limitations": sorted(set(limitations))[:4],
    }


def _estimate_tax_loss(tax_lots: list[TaxLot]) -> float:
    total_loss = Decimal("0")
    for lot in tax_lots:
        holding = lot.holding
        if holding is None or holding.quantity <= 0:
            continue
        lot_current_value = holding.market_value * (lot.quantity / holding.quantity)
        gain_loss = lot_current_value - lot.cost_basis
        if gain_loss < 0:
            total_loss += abs(gain_loss)
    return float(total_loss.quantize(Decimal("0.01")))


def _score_value(scores, label: str) -> int | None:
    for score in scores:
        if score.label.lower() == label.lower():
            return score.value
    return None


def _status_count(entries: list, status: str) -> int:
    return sum(1 for entry in entries if entry.status == status)


def _open_action_count(action_plans: list[ActionPlan]) -> int:
    return sum(1 for plan in action_plans if plan.status != "completed" and plan.dismissed_at is None)


def _completed_action_count(action_plans: list[ActionPlan]) -> int:
    return sum(1 for plan in action_plans if plan.status == "completed")


def _data_quality(holdings: list, has_provider_data: bool, is_stale: bool) -> str:
    if not holdings:
        return "limited"
    if is_stale:
        return "stale"
    if has_provider_data:
        return "mixed_user_and_provider"
    return "user_entered"


def _provider_status(status: str | None, has_provider_data: bool) -> str:
    if status:
        return status
    return "manual_only" if not has_provider_data else "unknown"


def _holding_label(holding) -> str | None:
    if holding is None:
        return None
    return f"{holding.symbol} ${float(holding.market_value):,.0f}"


def _liability_label(liability) -> str | None:
    if liability is None:
        return None
    return f"{liability.name} ${float(liability.balance):,.0f}"


def _evidence(
    label: str,
    value: str,
    source_name: str,
    data_as_of: str | None,
    retrieved_at: str | None,
    is_sample_data: bool,
    data_quality: str,
    provider_status: str,
    is_stale: bool,
    limitations: list[str] | None = None,
) -> AssistantEvidenceItem:
    return AssistantEvidenceItem(
        label=label,
        value=value,
        source_name=source_name,
        data_as_of=data_as_of,
        retrieved_at=retrieved_at,
        is_sample_data=is_sample_data,
        data_quality=data_quality,
        provider_status=provider_status,
        is_stale=is_stale,
        limitations=limitations or [],
    )


def _dedupe_sources(sources: list[SourceMetadata]) -> list[SourceMetadata]:
    seen: set[tuple[str, str | None]] = set()
    deduped: list[SourceMetadata] = []
    for source in sources:
        key = (source.name, source.as_of)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(source)
    return deduped


def _dt_or_date_iso(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def _safe_datetime(value) -> datetime:
    if value is None:
        return datetime.min.replace(tzinfo=UTC)
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time(), tzinfo=UTC)
    return datetime.min.replace(tzinfo=UTC)


def _to_float(value) -> float:
    return 0.0 if value is None else float(value)
