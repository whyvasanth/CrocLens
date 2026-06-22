from datetime import date
from decimal import Decimal
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import Asset, Holding, Liability, Portfolio, User
from app.schemas.api import (
    AssetDetailMetric,
    AssetDetailResponse,
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
    name="CrocLens portfolio records",
    freshness="User-entered financial snapshot",
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


def get_user_asset_detail(db: Session, user: User, asset_id: str) -> AssetDetailResponse | None:
    holding = _get_user_holding_by_public_id(db, user, asset_id)
    if holding is None:
        return None

    return _build_holding_detail_response(holding, _user_total_market_value(db, user))


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


def _get_user_holding_by_public_id(db: Session, user: User, asset_id: str) -> Holding | None:
    return db.scalar(
        select(Holding)
        .join(Holding.portfolio)
        .where(Portfolio.user_id == user.id)
        .where(or_(Holding.id == asset_id, Holding.asset_id == asset_id))
        .order_by(Holding.created_at.asc())
    )


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


def _build_holding_detail_response(holding: Holding, total_market_value: float) -> AssetDetailResponse:
    market_value = _to_float(holding.market_value)
    allocation_percent = 0 if total_market_value <= 0 else round((market_value / total_market_value) * 100, 2)
    asset_type = holding.asset.asset_type
    risk_level = ASSET_RISK_LEVELS.get(asset_type, "medium")
    quantity = _to_float(holding.quantity)

    return AssetDetailResponse(
        id=holding.id,
        symbol=holding.asset.symbol,
        name=holding.asset.name,
        category=_asset_detail_category(asset_type),
        asset_type=asset_type,
        current_value=market_value,
        allocation_percent=allocation_percent,
        risk_level=risk_level,
        portfolio_role=_portfolio_role_text(asset_type, allocation_percent),
        headline=f"{holding.asset.name} is part of your tracked {asset_type.lower()} view.",
        what_this_is=_asset_explanation(asset_type),
        why_it_matters=_why_asset_matters(asset_type),
        risk_explanation=_risk_detail(asset_type, risk_level),
        liquidity_explanation=_liquidity_detail(asset_type),
        tax_complexity_explanation=_tax_complexity_detail(asset_type),
        income_potential_explanation=_income_potential_detail(asset_type),
        what_to_watch=_watch_items(asset_type),
        beginner_takeaway=(
            f"Based on your entered value, {holding.asset.symbol} represents "
            f"{allocation_percent:.1f}% of your tracked assets."
        ),
        safe_next_steps=[
            "Consider reviewing whether this holding still matches your goal, time horizon, and comfort with risk.",
            "You may want to compare its size with the rest of your tracked assets before making changes.",
            "If taxes or retirement rules could apply, consider discussing decisions with a qualified professional.",
        ],
        key_metrics=[
            AssetDetailMetric(
                label="Tracked value",
                value=_format_money(market_value),
                explanation="This is the value you entered or last saved in CrocLens.",
                tone="green",
            ),
            AssetDetailMetric(
                label="Portfolio share",
                value=f"{allocation_percent:.1f}%",
                explanation="This shows how much of your tracked asset total this holding represents.",
                tone="gold" if allocation_percent >= 25 else "neutral",
            ),
            AssetDetailMetric(
                label="Quantity",
                value=_format_quantity(quantity),
                explanation="Quantity helps CrocLens value public holdings once live prices are connected.",
                tone="neutral",
            ),
            AssetDetailMetric(
                label="Cost basis",
                value=_format_money(_to_float(holding.cost_basis)) if holding.cost_basis is not None else "Not entered",
                explanation="Cost basis can help explain gains, losses, and tax context later.",
                tone="blue",
            ),
        ],
        confidence="medium",
        data_limitations=[
            "This detail page uses your manually entered portfolio record.",
            "Live provider valuation is not applied to this holding detail yet.",
            "CrocLens does not verify manually entered values.",
        ],
        source=PERSISTED_SOURCE,
        educational_disclaimer=EDUCATIONAL_DISCLAIMER,
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


def _asset_detail_category(asset_type: str) -> str:
    if asset_type in {"Stocks", "ETFs", "Mutual Funds"}:
        return "stock_etf"
    if asset_type == "Crypto":
        return "crypto"
    if asset_type == "Real Estate":
        return "real_estate"
    if asset_type == "Retirement":
        return "retirement"
    if asset_type == "Cash":
        return "cash"
    if asset_type in {"Bonds", "Treasuries"}:
        return "bond"
    return "other"


def _portfolio_role_text(asset_type: str, allocation_percent: float) -> str:
    if allocation_percent >= 30:
        return f"This is a large part of your tracked {asset_type.lower()} picture, so changes here can noticeably affect net worth."
    if allocation_percent >= 10:
        return f"This is a meaningful part of your tracked assets and is worth reviewing alongside your goals."
    if allocation_percent > 0:
        return "This is a smaller part of your tracked assets, but it still contributes to the full wealth picture."
    return "This holding is tracked, but its saved value is currently zero."


def _why_asset_matters(asset_type: str) -> str:
    explanations = {
        "Cash": "Cash can support emergencies and short-term needs, but it may lose purchasing power when inflation is high.",
        "Crypto": "Crypto can create large swings in net worth because prices can move sharply.",
        "ETFs": "ETFs can provide broad exposure in one holding, which can make diversification easier to understand.",
        "Mutual Funds": "Mutual funds can provide diversified exposure, but fees, taxes, and account type can matter.",
        "Real Estate": "Real estate can be a major part of net worth, but its value is less liquid and harder to price daily.",
        "Retirement": "Retirement assets matter because account rules, contribution habits, and time horizon affect long-term planning.",
        "Stocks": "Stocks can drive growth and volatility because they represent ownership in individual companies.",
        "Bonds": "Bonds can add income and interest-rate sensitivity, which behaves differently from stocks.",
        "Treasuries": "Treasuries can provide rate and safety context, but yields and bond prices can still change.",
    }
    return explanations.get(asset_type, "This record matters because CrocLens uses it to build your full net worth view.")


def _risk_detail(asset_type: str, risk_level: str) -> str:
    return (
        f"CrocLens currently labels this {asset_type.lower()} record as {risk_level} risk based on the asset type. "
        "This is an educational estimate, not a personalized risk rating."
    )


def _liquidity_detail(asset_type: str) -> str:
    details = {
        "Cash": "Cash is usually the easiest asset to access.",
        "Real Estate": "Real estate is usually less liquid because selling can take time and includes transaction costs.",
        "Retirement": "Retirement account liquidity depends on account rules, age, taxes, and possible penalties.",
        "Crypto": "Crypto can often be traded quickly, but platform access, volatility, and fees can affect practical liquidity.",
        "Bonds": "Bond liquidity depends on the bond type, market conditions, and whether it is held through a fund.",
        "Treasuries": "Treasury liquidity is often strong, but timing and price changes still matter.",
    }
    return details.get(asset_type, "Public market holdings are often easier to sell than private assets, but prices can move.")


def _tax_complexity_detail(asset_type: str) -> str:
    details = {
        "Cash": "Cash tax complexity is usually lower, though interest income can still be taxable.",
        "Real Estate": "Real estate can involve property taxes, mortgage interest, depreciation, and capital gains rules.",
        "Retirement": "Retirement accounts can have contribution limits, withdrawal rules, and tax treatment differences.",
        "Crypto": "Crypto can create tax complexity because trades, conversions, staking, and transfers may need records.",
        "Bonds": "Bond tax treatment can vary by issuer, account type, and interest income.",
        "Treasuries": "Treasury interest may have different federal and state tax treatment.",
    }
    return details.get(asset_type, "Tax impact depends on account type, holding period, gains or losses, and local rules.")


def _income_potential_detail(asset_type: str) -> str:
    details = {
        "Cash": "Cash can earn interest, but rates can change.",
        "Real Estate": "Real estate may produce rental income, but expenses and vacancies can reduce it.",
        "Retirement": "Retirement holdings may produce dividends or interest depending on the investments inside the account.",
        "Crypto": "Crypto income potential is uncertain and may involve additional risk or platform complexity.",
        "Bonds": "Bonds are often used for interest income, though rates and credit risk matter.",
        "Treasuries": "Treasuries can provide interest income backed by the U.S. government, but yields change over time.",
        "ETFs": "Some ETFs pay dividends or interest, depending on what they hold.",
        "Mutual Funds": "Some mutual funds distribute dividends, interest, or capital gains.",
        "Stocks": "Some stocks pay dividends, but many do not and payouts can change.",
    }
    return details.get(asset_type, "Income potential depends on the asset, account type, fees, and market conditions.")


def _watch_items(asset_type: str) -> list[str]:
    common = [
        "How large this position is compared with the rest of your tracked assets.",
        "Whether the saved value is current enough for decisions or only a rough estimate.",
    ]
    by_type = {
        "Cash": ["Whether emergency savings covers the number of months you want."],
        "Crypto": ["Whether volatility could make this position feel larger than expected during market swings."],
        "Real Estate": ["Whether the estimate reflects recent local housing changes and selling costs."],
        "Retirement": ["Whether contributions, employer match, and time horizon still match your plan."],
        "Bonds": ["How interest-rate changes could affect bond prices or bond fund values."],
        "Treasuries": ["How yield changes could affect income and price if sold before maturity."],
    }
    return common + by_type.get(asset_type, ["Fees, concentration, and how this asset fits your goal."])


def _format_money(value: float) -> str:
    return f"${value:,.2f}"


def _format_quantity(value: float) -> str:
    if value == 0:
        return "Not entered"
    return f"{value:,.4f}".rstrip("0").rstrip(".")


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
