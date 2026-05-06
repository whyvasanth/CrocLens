from app.schemas.api import SourceMetadata, TaxInsightResponse, TaxLotResponse, TaxOpportunityResponse
from app.services.mock_data import EDUCATIONAL_DISCLAIMER


TAX_SOURCE = SourceMetadata(
    name="CrocLens sample tax lots",
    freshness="Sample tax lot data for education",
    as_of="2026-05-06",
)


def get_tax_insights() -> TaxInsightResponse:
    tax_lots = [
        _tax_lot(
            lot_id="lot_vti_2024",
            symbol="VTI",
            asset_name="Vanguard Total Stock Market ETF",
            quantity=28,
            purchase_date="2024-02-15",
            cost_basis=6900,
            current_value=7330,
            holding_period_days=811,
        ),
        _tax_lot(
            lot_id="lot_btc_2025",
            symbol="BTC",
            asset_name="Bitcoin sample lot",
            quantity=0.18,
            purchase_date="2025-11-12",
            cost_basis=13800,
            current_value=11955,
            holding_period_days=175,
        ),
        _tax_lot(
            lot_id="lot_agg_2025",
            symbol="AGG",
            asset_name="US bond ETF sample lot",
            quantity=40,
            purchase_date="2025-06-03",
            cost_basis=4100,
            current_value=3940,
            holding_period_days=337,
        ),
    ]

    total_gain = round(sum(max(lot.unrealized_gain_loss, 0) for lot in tax_lots), 2)
    total_loss = round(abs(sum(min(lot.unrealized_gain_loss, 0) for lot in tax_lots)), 2)

    opportunities = [
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

    return TaxInsightResponse(
        headline="Two sample lots show unrealized losses that may be worth learning about.",
        beginner_summary=(
            "A tax lot is one purchase record. CrocLens groups lots so you can understand gains, losses, "
            "holding periods, and recordkeeping before any tax decision."
        ),
        total_unrealized_gain=total_gain,
        total_unrealized_loss=total_loss,
        tax_lots=tax_lots,
        harvesting_opportunities=opportunities,
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


def _tax_lot(
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
