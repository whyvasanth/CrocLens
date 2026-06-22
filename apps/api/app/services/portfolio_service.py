from datetime import date
from decimal import Decimal
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Asset, Holding, Liability, Portfolio, User
from app.schemas.api import (
    AssetResponse,
    DeleteRecordResponse,
    HoldingCreateRequest,
    HoldingResponse,
    HoldingUpdateRequest,
    LiabilityCreateRequest,
    LiabilityResponse,
    LiabilityUpdateRequest,
    PortfolioRecordsResponse,
    PortfolioSummaryResponse,
    SourceMetadata,
)
from app.services.portfolio_calculations import (
    AssetPosition,
    LiabilityPosition,
    calculate_portfolio_summary,
)

EDUCATIONAL_DISCLAIMER = "This is educational information, not financial advice."

PERSISTED_SOURCE = SourceMetadata(
    name="CrocLens PostgreSQL portfolio records",
    freshness="User-entered local development data",
    as_of="2026-06-22",
)

ASSET_RISK_LEVELS = {
    "Cash": "low",
    "Treasuries": "low",
    "Bonds": "medium",
    "ETFs": "medium",
    "Mutual Funds": "medium",
    "Stocks": "medium",
    "Real Estate": "medium",
    "Retirement": "medium",
    "Crypto": "high",
}


def get_or_create_default_portfolio(db: Session, user: User) -> Portfolio:
    portfolio = db.scalar(select(Portfolio).where(Portfolio.user_id == user.id).order_by(Portfolio.created_at.asc()))
    if portfolio is not None:
        return portfolio

    portfolio = Portfolio(
        id=str(uuid4()),
        user_id=user.id,
        name="My CrocLens Portfolio",
        base_currency="USD",
    )
    db.add(portfolio)
    db.flush()
    return portfolio


def get_portfolio_records(db: Session, user: User) -> PortfolioRecordsResponse:
    holdings = list_user_holdings(db, user)
    liabilities = list_user_liabilities(db, user)
    return PortfolioRecordsResponse(
        holdings=holdings,
        liabilities=liabilities,
        summary=get_user_portfolio_summary(db, user),
    )


def get_user_portfolio_summary(db: Session, user: User) -> PortfolioSummaryResponse:
    holdings = _load_user_holdings(db, user)
    liabilities = _load_user_liabilities(db, user)
    calculation = calculate_portfolio_summary(
        assets=[
            AssetPosition(asset_class=holding.asset.asset_type, market_value=_to_float(holding.market_value))
            for holding in holdings
        ],
        liabilities=[
            LiabilityPosition(
                liability_type=liability.liability_type,
                balance=_to_float(liability.balance),
                interest_rate=_to_float(liability.interest_rate) if liability.interest_rate is not None else None,
            )
            for liability in liabilities
        ],
    )

    return PortfolioSummaryResponse(
        user_name=user.full_name or user.email.split("@")[0],
        total_assets=calculation.total_assets,
        total_liabilities=calculation.total_liabilities,
        net_worth=calculation.net_worth,
        allocation=calculation.allocation,
        debt_impact=calculation.debt_impact,
        scores=calculation.scores,
        sources=[PERSISTED_SOURCE],
        educational_disclaimer=EDUCATIONAL_DISCLAIMER,
    )


def list_user_assets(db: Session, user: User) -> list[AssetResponse]:
    holdings = list_user_holdings(db, user)
    return [
        AssetResponse(
            id=holding.id,
            symbol=holding.symbol,
            name=holding.name,
            asset_type=holding.asset_type,
            current_price=None,
            market_value=holding.market_value,
            allocation_percent=holding.allocation_percent,
            risk_level=ASSET_RISK_LEVELS.get(holding.asset_type, "medium"),
            beginner_explanation=_asset_explanation(holding.asset_type),
            source=holding.source,
        )
        for holding in holdings
    ]


def list_user_holdings(db: Session, user: User) -> list[HoldingResponse]:
    holdings = _load_user_holdings(db, user)
    total_market_value = sum(_to_float(holding.market_value) for holding in holdings)
    return [_build_holding_response(holding, total_market_value) for holding in holdings]


def create_holding(db: Session, user: User, request: HoldingCreateRequest) -> HoldingResponse:
    portfolio = get_or_create_default_portfolio(db, user)
    asset = _get_or_create_asset(
        db=db,
        symbol=request.symbol,
        name=request.name,
        asset_type=request.asset_type,
    )
    holding = Holding(
        id=str(uuid4()),
        portfolio_id=portfolio.id,
        asset_id=asset.id,
        account_name=_clean_optional_text(request.account_name),
        quantity=_to_decimal(request.quantity),
        cost_basis=_optional_decimal(request.cost_basis),
        market_value=_to_decimal(request.market_value),
        as_of_date=_parse_date(request.as_of_date),
    )
    db.add(holding)
    db.flush()
    return _build_holding_response(holding, _user_total_market_value(db, user))


def update_holding(db: Session, user: User, holding_id: str, request: HoldingUpdateRequest) -> HoldingResponse:
    holding = _get_user_holding_or_404(db, user, holding_id)
    if request.symbol is not None or request.name is not None or request.asset_type is not None:
        holding.asset = _get_or_create_asset(
            db=db,
            symbol=request.symbol or holding.asset.symbol,
            name=request.name or holding.asset.name,
            asset_type=request.asset_type or holding.asset.asset_type,
        )
    if request.account_name is not None:
        holding.account_name = _clean_optional_text(request.account_name)
    if request.quantity is not None:
        holding.quantity = _to_decimal(request.quantity)
    if request.cost_basis is not None:
        holding.cost_basis = _to_decimal(request.cost_basis)
    if request.market_value is not None:
        holding.market_value = _to_decimal(request.market_value)
    if request.as_of_date is not None:
        holding.as_of_date = _parse_date(request.as_of_date)

    db.add(holding)
    db.flush()
    return _build_holding_response(holding, _user_total_market_value(db, user))


def delete_holding(db: Session, user: User, holding_id: str) -> DeleteRecordResponse:
    holding = _get_user_holding_or_404(db, user, holding_id)
    db.delete(holding)
    db.flush()
    return DeleteRecordResponse(status="deleted", id=holding_id)


def list_user_liabilities(db: Session, user: User) -> list[LiabilityResponse]:
    return [_build_liability_response(liability) for liability in _load_user_liabilities(db, user)]


def create_liability(db: Session, user: User, request: LiabilityCreateRequest) -> LiabilityResponse:
    liability = Liability(
        id=str(uuid4()),
        user_id=user.id,
        name=request.name.strip(),
        liability_type=request.liability_type,
        balance=_to_decimal(request.balance),
        interest_rate=_optional_decimal(request.interest_rate),
        minimum_payment=_optional_decimal(request.minimum_payment),
        due_day=request.due_day,
    )
    db.add(liability)
    db.flush()
    return _build_liability_response(liability)


def update_liability(
    db: Session,
    user: User,
    liability_id: str,
    request: LiabilityUpdateRequest,
) -> LiabilityResponse:
    liability = _get_user_liability_or_404(db, user, liability_id)
    if request.name is not None:
        liability.name = request.name.strip()
    if request.liability_type is not None:
        liability.liability_type = request.liability_type
    if request.balance is not None:
        liability.balance = _to_decimal(request.balance)
    if request.interest_rate is not None:
        liability.interest_rate = _to_decimal(request.interest_rate)
    if request.minimum_payment is not None:
        liability.minimum_payment = _to_decimal(request.minimum_payment)
    if request.due_day is not None:
        liability.due_day = request.due_day

    db.add(liability)
    db.flush()
    return _build_liability_response(liability)


def delete_liability(db: Session, user: User, liability_id: str) -> DeleteRecordResponse:
    liability = _get_user_liability_or_404(db, user, liability_id)
    db.delete(liability)
    db.flush()
    return DeleteRecordResponse(status="deleted", id=liability_id)


def create_manual_asset_holdings_for_user(db: Session, user: User, manual_assets: list) -> None:
    for manual_asset in manual_assets:
        create_holding(
            db=db,
            user=user,
            request=HoldingCreateRequest(
                symbol=_symbol_from_label(manual_asset.label),
                name=manual_asset.label,
                asset_type=_coerce_asset_type(manual_asset.asset_class),
                account_name="Signup manual entry",
                quantity=0,
                market_value=manual_asset.estimated_value,
                as_of_date=date.today().isoformat(),
            ),
        )


def _load_user_holdings(db: Session, user: User) -> list[Holding]:
    return list(
        db.scalars(
            select(Holding)
            .join(Holding.portfolio)
            .where(Portfolio.user_id == user.id)
            .order_by(Holding.created_at.asc())
        )
    )


def _load_user_liabilities(db: Session, user: User) -> list[Liability]:
    return list(
        db.scalars(
            select(Liability)
            .where(Liability.user_id == user.id)
            .order_by(Liability.created_at.asc())
        )
    )


def _get_user_holding_or_404(db: Session, user: User, holding_id: str) -> Holding:
    holding = db.scalar(
        select(Holding)
        .join(Holding.portfolio)
        .where(Holding.id == holding_id)
        .where(Portfolio.user_id == user.id)
    )
    if holding is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Holding was not found.")
    return holding


def _get_user_liability_or_404(db: Session, user: User, liability_id: str) -> Liability:
    liability = db.scalar(
        select(Liability)
        .where(Liability.id == liability_id)
        .where(Liability.user_id == user.id)
    )
    if liability is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Liability was not found.")
    return liability


def _get_or_create_asset(db: Session, symbol: str, name: str, asset_type: str) -> Asset:
    normalized_symbol = symbol.strip().upper()
    normalized_asset_type = asset_type.strip()
    asset = db.scalar(
        select(Asset)
        .where(Asset.symbol == normalized_symbol)
        .where(Asset.asset_type == normalized_asset_type)
    )
    if asset is not None:
        if asset.name != name.strip():
            asset.name = name.strip()
            db.add(asset)
        return asset

    asset = Asset(
        id=str(uuid4()),
        symbol=normalized_symbol,
        name=name.strip(),
        asset_type=normalized_asset_type,
        currency="USD",
        data_source="manual_entry",
    )
    db.add(asset)
    db.flush()
    return asset


def _build_holding_response(holding: Holding, total_market_value: float) -> HoldingResponse:
    market_value = _to_float(holding.market_value)
    allocation_percent = 0 if total_market_value <= 0 else round((market_value / total_market_value) * 100, 2)
    return HoldingResponse(
        id=holding.id,
        portfolio_id=holding.portfolio_id,
        asset_id=holding.asset_id,
        symbol=holding.asset.symbol,
        name=holding.asset.name,
        asset_type=holding.asset.asset_type,
        account_name=holding.account_name,
        quantity=_to_float(holding.quantity),
        cost_basis=_to_float(holding.cost_basis) if holding.cost_basis is not None else None,
        market_value=market_value,
        allocation_percent=allocation_percent,
        as_of_date=holding.as_of_date.isoformat() if holding.as_of_date else None,
        source=PERSISTED_SOURCE,
    )


def _build_liability_response(liability: Liability) -> LiabilityResponse:
    return LiabilityResponse(
        id=liability.id,
        name=liability.name,
        liability_type=liability.liability_type,
        balance=_to_float(liability.balance),
        interest_rate=_to_float(liability.interest_rate) if liability.interest_rate is not None else None,
        minimum_payment=_to_float(liability.minimum_payment) if liability.minimum_payment is not None else None,
        due_day=liability.due_day,
        source=PERSISTED_SOURCE,
    )


def _user_total_market_value(db: Session, user: User) -> float:
    return sum(_to_float(holding.market_value) for holding in _load_user_holdings(db, user))


def _asset_explanation(asset_type: str) -> str:
    explanations = {
        "Cash": "Cash is usually stable and easy to access, but inflation can reduce purchasing power.",
        "Crypto": "Crypto can move sharply in price, so CrocLens treats it as higher risk.",
        "ETFs": "ETFs are baskets of investments that can make diversification easier.",
        "Mutual Funds": "Mutual funds pool many investments, but fees and tax treatment can vary.",
        "Real Estate": "Real estate can build equity but is usually less liquid than public investments.",
        "Retirement": "Retirement accounts are long-term accounts with tax rules and contribution limits.",
        "Stocks": "Stocks represent ownership in companies and can move up and down with markets.",
        "Bonds": "Bonds are loans to issuers and can be affected by interest rates and credit risk.",
        "Treasuries": "Treasuries are U.S. government debt and are often used for rate and safety context.",
    }
    return explanations.get(asset_type, "This manually tracked asset is included in your net worth view.")


def _parse_date(value: str | None) -> date | None:
    if value is None or not value.strip():
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Date must use YYYY-MM-DD.") from exc


def _symbol_from_label(label: str) -> str:
    cleaned = "".join(character if character.isalnum() else "_" for character in label.upper()).strip("_")
    return cleaned[:40] or "MANUAL"


def _coerce_asset_type(asset_class: str) -> str:
    allowed = {
        "Stocks",
        "ETFs",
        "Mutual Funds",
        "Crypto",
        "Real Estate",
        "Cash",
        "Bonds",
        "Treasuries",
        "Retirement",
        "Other",
    }
    normalized = asset_class.strip()
    return normalized if normalized in allowed else "Other"


def _clean_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def _to_decimal(value: float | int | Decimal) -> Decimal:
    return Decimal(str(value))


def _optional_decimal(value: float | int | Decimal | None) -> Decimal | None:
    return None if value is None else _to_decimal(value)


def _to_float(value: Decimal | float | int | None) -> float:
    return 0.0 if value is None else float(value)
