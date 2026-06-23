from datetime import date
from decimal import Decimal
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Holding, Portfolio, TaxLot, User
from app.schemas.api import (
    DeleteRecordResponse,
    SourceMetadata,
    TaxInsightResponse,
    TaxLotCreateRequest,
    TaxLotResponse,
    TaxLotUpdateRequest,
    TaxOpportunityResponse,
)
from app.services.mock_data import EDUCATIONAL_DISCLAIMER


TAX_SOURCE = SourceMetadata(
    name="CrocLens sample tax lots",
    freshness="Sample tax lot data for education",
    as_of="2026-05-06",
)

PERSISTED_TAX_SOURCE = SourceMetadata(
    name="CrocLens tax lot records",
    freshness="Saved user tax lots",
    as_of=date.today().isoformat(),
)


def get_tax_insights(db: Session | None = None, user: User | None = None) -> TaxInsightResponse:
    if db is None or user is None:
        return _sample_tax_insights()

    lots = _load_user_tax_lots(db, user)
    tax_lots = [_build_tax_lot_response(lot) for lot in lots]
    total_gain = round(sum(max(lot.unrealized_gain_loss, 0) for lot in tax_lots), 2)
    total_loss = round(abs(sum(min(lot.unrealized_gain_loss, 0) for lot in tax_lots)), 2)
    opportunities = _opportunities_for(tax_lots)

    return TaxInsightResponse(
        headline=(
            "Your saved tax lots are ready for educational review."
            if tax_lots
            else "Add tax lots to learn about holding periods and unrealized gains or losses."
        ),
        beginner_summary=(
            "A tax lot is one purchase record. CrocLens uses your saved lots to explain gains, losses, and holding periods without giving tax advice."
        ),
        total_unrealized_gain=total_gain,
        total_unrealized_loss=total_loss,
        tax_lots=tax_lots,
        harvesting_opportunities=opportunities,
        short_term_vs_long_term_explanation=(
            "In the US, assets held for one year or less are generally short-term, while assets held longer than one year are generally long-term. Tax treatment can differ, so verify with a qualified professional."
        ),
        wash_sale_warning=(
            "Wash-sale rules can limit loss deductions if you sell at a loss and buy a substantially identical security within the rule window. Review current rules with a qualified tax professional before acting."
        ),
        confidence="medium",
        data_limitations=[
            "Uses saved CrocLens tax lot records.",
            "Does not know your full transaction history, tax bracket, filing status, or state taxes.",
            "This is tax education, not tax advice.",
        ],
        sources=[PERSISTED_TAX_SOURCE],
        educational_disclaimer=EDUCATIONAL_DISCLAIMER,
    )


def create_tax_lot(db: Session, user: User, request: TaxLotCreateRequest) -> TaxLotResponse:
    holding = _get_user_holding_or_404(db, user, request.holding_id)
    lot = TaxLot(
        id=str(uuid4()),
        holding_id=holding.id,
        acquired_date=_parse_date(request.acquired_date),
        quantity=_to_decimal(request.quantity),
        cost_basis=_to_decimal(request.cost_basis),
        account_tax_type=request.account_tax_type.strip(),
    )
    db.add(lot)
    db.flush()
    return _build_tax_lot_response(lot)


def update_tax_lot(db: Session, user: User, lot_id: str, request: TaxLotUpdateRequest) -> TaxLotResponse:
    lot = _get_user_tax_lot_or_404(db, user, lot_id)
    if request.acquired_date is not None:
        lot.acquired_date = _parse_date(request.acquired_date)
    if request.quantity is not None:
        lot.quantity = _to_decimal(request.quantity)
    if request.cost_basis is not None:
        lot.cost_basis = _to_decimal(request.cost_basis)
    if request.account_tax_type is not None:
        lot.account_tax_type = request.account_tax_type.strip()

    db.add(lot)
    db.flush()
    return _build_tax_lot_response(lot)


def delete_tax_lot(db: Session, user: User, lot_id: str) -> DeleteRecordResponse:
    lot = _get_user_tax_lot_or_404(db, user, lot_id)
    db.delete(lot)
    db.flush()
    return DeleteRecordResponse(status="deleted", id=lot_id)


def _sample_tax_insights() -> TaxInsightResponse:
    tax_lots = [
        _sample_tax_lot("lot_vti_2024", "VTI", "Vanguard Total Stock Market ETF", 28, "2024-02-15", 6900, 7330, 811),
        _sample_tax_lot("lot_btc_2025", "BTC", "Bitcoin sample lot", 0.18, "2025-11-12", 13800, 11955, 175),
        _sample_tax_lot("lot_agg_2025", "AGG", "US bond ETF sample lot", 40, "2025-06-03", 4100, 3940, 337),
    ]
    total_gain = round(sum(max(lot.unrealized_gain_loss, 0) for lot in tax_lots), 2)
    total_loss = round(abs(sum(min(lot.unrealized_gain_loss, 0) for lot in tax_lots)), 2)

    return TaxInsightResponse(
        headline="Two sample lots show unrealized losses that may be worth learning about.",
        beginner_summary=(
            "A tax lot is one purchase record. CrocLens groups lots so you can understand gains, losses, "
            "holding periods, and recordkeeping before any tax decision."
        ),
        total_unrealized_gain=total_gain,
        total_unrealized_loss=total_loss,
        tax_lots=tax_lots,
        harvesting_opportunities=_sample_opportunities(),
        short_term_vs_long_term_explanation=(
            "In the US, assets held for one year or less are generally short-term, while assets held longer than "
            "one year are generally long-term. Tax treatment can differ, so verify with a qualified professional."
        ),
        wash_sale_warning=(
            "Wash-sale rules can limit loss deductions if you sell at a loss and buy a substantially identical "
            "security within the rule window. Crypto rules and securities rules can differ, so review current rules."
        ),
        confidence="medium",
        data_limitations=[
            "Uses sample tax lots only.",
            "Does not know the user's tax bracket, filing status, state taxes, or full transaction history.",
            "This is tax education, not tax advice.",
        ],
        sources=[TAX_SOURCE],
        educational_disclaimer=EDUCATIONAL_DISCLAIMER,
    )


def _build_tax_lot_response(lot: TaxLot) -> TaxLotResponse:
    holding = _get_holding_for_lot(lot)
    current_value = _estimated_lot_current_value(lot, holding)
    cost_basis = _to_float(lot.cost_basis)
    holding_period_days = max(0, (date.today() - lot.acquired_date).days)
    gain_loss = round(current_value - cost_basis, 2)
    holding_term = "long_term" if holding_period_days > 365 else "short_term"
    gain_word = "gain" if gain_loss >= 0 else "loss"

    return TaxLotResponse(
        id=lot.id,
        symbol=holding.asset.symbol,
        asset_name=holding.asset.name,
        quantity=_to_float(lot.quantity),
        purchase_date=lot.acquired_date.isoformat(),
        cost_basis=cost_basis,
        current_value=current_value,
        unrealized_gain_loss=gain_loss,
        holding_period_days=holding_period_days,
        holding_term=holding_term,
        beginner_explanation=(
            f"This lot currently shows an unrealized {gain_word}. It is not taxable just because CrocLens displays it; "
            "tax events usually depend on transactions and tax rules."
        ),
    )


def _estimated_lot_current_value(lot: TaxLot, holding: Holding) -> float:
    holding_quantity = _to_float(holding.quantity)
    if holding_quantity <= 0:
        return 0
    return round(_to_float(holding.market_value) * (_to_float(lot.quantity) / holding_quantity), 2)


def _opportunities_for(tax_lots: list[TaxLotResponse]) -> list[TaxOpportunityResponse]:
    return [
        TaxOpportunityResponse(
            id=f"opp_{lot.id}",
            symbol=lot.symbol,
            title=f"Review unrealized loss for {lot.symbol}",
            estimated_unrealized_loss=abs(lot.unrealized_gain_loss),
            explanation=(
                "This saved lot has an unrealized loss. CrocLens can explain the concept, but it cannot tell you to sell or claim a tax strategy."
            ),
            safe_next_steps=[
                "Consider reviewing purchase records and transaction history.",
                "You may want to research tax-loss harvesting basics.",
                "This may be worth discussing with a tax professional before acting.",
            ],
        )
        for lot in tax_lots
        if lot.unrealized_gain_loss < 0
    ]


def _sample_opportunities() -> list[TaxOpportunityResponse]:
    return [
        TaxOpportunityResponse(
            id="opp_btc_loss_review",
            symbol="BTC",
            title="Review unrealized crypto loss recordkeeping",
            estimated_unrealized_loss=1845,
            explanation=(
                "This sample lot has an unrealized loss. CrocLens can explain the concept, but it cannot tell you "
                "to sell or claim a tax strategy."
            ),
            safe_next_steps=[
                "Consider reviewing purchase records and transaction history.",
                "You may want to research tax-loss harvesting basics.",
                "This may be worth discussing with a tax professional before acting.",
            ],
        ),
        TaxOpportunityResponse(
            id="opp_agg_loss_review",
            symbol="AGG",
            title="Review bond ETF loss and holding period",
            estimated_unrealized_loss=160,
            explanation="Small sample losses may still be useful for learning how lots and holding periods work.",
            safe_next_steps=[
                "Consider comparing the lot's holding period with your broader plan.",
                "Research wash-sale rules before replacing similar securities.",
            ],
        ),
    ]


def _sample_tax_lot(
    lot_id: str,
    symbol: str,
    asset_name: str,
    quantity: float,
    purchase_date: str,
    cost_basis: float,
    current_value: float,
    holding_period_days: int,
) -> TaxLotResponse:
    gain_loss = round(current_value - cost_basis, 2)
    holding_term = "long_term" if holding_period_days > 365 else "short_term"
    gain_word = "gain" if gain_loss >= 0 else "loss"
    return TaxLotResponse(
        id=lot_id,
        symbol=symbol,
        asset_name=asset_name,
        quantity=quantity,
        purchase_date=purchase_date,
        cost_basis=cost_basis,
        current_value=current_value,
        unrealized_gain_loss=gain_loss,
        holding_period_days=holding_period_days,
        holding_term=holding_term,
        beginner_explanation=(
            f"This lot currently shows an unrealized {gain_word}. It is not taxable just because CrocLens displays it; "
            "tax events usually depend on transactions and tax rules."
        ),
    )


def _load_user_tax_lots(db: Session, user: User) -> list[TaxLot]:
    return list(
        db.scalars(
            select(TaxLot)
            .join(Holding, TaxLot.holding_id == Holding.id)
            .join(Portfolio, Holding.portfolio_id == Portfolio.id)
            .where(Portfolio.user_id == user.id)
            .order_by(TaxLot.acquired_date.asc())
        )
    )


def _get_user_holding_or_404(db: Session, user: User, holding_id: str) -> Holding:
    holding = db.scalar(
        select(Holding)
        .join(Portfolio, Holding.portfolio_id == Portfolio.id)
        .where(Holding.id == holding_id)
        .where(Portfolio.user_id == user.id)
    )
    if holding is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Holding was not found.")
    return holding


def _get_user_tax_lot_or_404(db: Session, user: User, lot_id: str) -> TaxLot:
    lot = db.scalar(
        select(TaxLot)
        .join(Holding, TaxLot.holding_id == Holding.id)
        .join(Portfolio, Holding.portfolio_id == Portfolio.id)
        .where(TaxLot.id == lot_id)
        .where(Portfolio.user_id == user.id)
    )
    if lot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tax lot was not found.")
    return lot


def _get_holding_for_lot(lot: TaxLot) -> Holding:
    holding = lot.holding
    if holding is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Tax lot is missing its holding.")
    return holding


def _parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Date must use YYYY-MM-DD.") from exc


def _to_decimal(value: float | int | Decimal) -> Decimal:
    return Decimal(str(value))


def _to_float(value: Decimal | float | int | None) -> float:
    return 0.0 if value is None else float(value)
