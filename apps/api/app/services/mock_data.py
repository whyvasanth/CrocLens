from app.schemas.api import (
    ActionPlanItem,
    ActionPlanResponse,
    AssetResponse,
    PortfolioSummaryResponse,
    SourceMetadata,
)
from app.services.portfolio_calculations import (
    AssetPosition,
    LiabilityPosition,
    calculate_portfolio_summary,
)

MOCK_SOURCE = SourceMetadata(
    name="CrocLens sample data",
    freshness="Calculated from Phase 6 sample positions",
    as_of="2026-05-05",
)

EDUCATIONAL_DISCLAIMER = "This is educational information, not financial advice."


def get_portfolio_summary() -> PortfolioSummaryResponse:
    calculation = calculate_portfolio_summary(
        assets=get_sample_asset_positions(),
        liabilities=get_sample_liability_positions(),
    )

    return PortfolioSummaryResponse(
        user_name="Maya",
        total_assets=calculation.total_assets,
        total_liabilities=calculation.total_liabilities,
        net_worth=calculation.net_worth,
        allocation=calculation.allocation,
        debt_impact=calculation.debt_impact,
        scores=calculation.scores,
        sources=[MOCK_SOURCE],
        educational_disclaimer=EDUCATIONAL_DISCLAIMER,
    )


def get_sample_asset_positions() -> list[AssetPosition]:
    return [
        AssetPosition(asset_class="Stocks", market_value=95_526),
        AssetPosition(asset_class="ETFs", market_value=79_056),
        AssetPosition(asset_class="Real Estate", market_value=72_468),
        AssetPosition(asset_class="Retirement", market_value=42_822),
        AssetPosition(asset_class="Cash", market_value=23_058),
        AssetPosition(asset_class="Crypto", market_value=16_470),
    ]


def get_sample_liability_positions() -> list[LiabilityPosition]:
    return [
        LiabilityPosition(liability_type="Mortgage", balance=106_000, interest_rate=0.061),
        LiabilityPosition(liability_type="Student loan", balance=6_100, interest_rate=0.045),
        LiabilityPosition(liability_type="Credit card", balance=2_500, interest_rate=0.199),
    ]


def list_assets() -> list[AssetResponse]:
    return [
        AssetResponse(
            id="asset_stock_bucket",
            symbol="STOCKS",
            name="Stock holdings",
            asset_type="Stocks",
            current_price=None,
            market_value=95_526,
            allocation_percent=29,
            risk_level="medium",
            beginner_explanation="Stocks represent ownership in companies and can move up and down with markets.",
            source=MOCK_SOURCE,
        ),
        AssetResponse(
            id="asset_etf_bucket",
            symbol="ETFS",
            name="ETF holdings",
            asset_type="ETFs",
            current_price=None,
            market_value=79_056,
            allocation_percent=24,
            risk_level="medium",
            beginner_explanation="ETFs are baskets of investments that can make diversification easier.",
            source=MOCK_SOURCE,
        ),
        AssetResponse(
            id="asset_real_estate",
            symbol="HOME",
            name="Real estate equity",
            asset_type="Real Estate",
            current_price=None,
            market_value=72_468,
            allocation_percent=22,
            risk_level="medium",
            beginner_explanation="Real estate can build equity but is usually less liquid than public investments.",
            source=MOCK_SOURCE,
        ),
        AssetResponse(
            id="asset_retirement",
            symbol="401K",
            name="Retirement accounts",
            asset_type="Retirement",
            current_price=None,
            market_value=42_822,
            allocation_percent=13,
            risk_level="medium",
            beginner_explanation="Retirement accounts are long-term accounts with tax rules and contribution limits.",
            source=MOCK_SOURCE,
        ),
        AssetResponse(
            id="asset_btc",
            symbol="BTC",
            name="Bitcoin",
            asset_type="Crypto",
            current_price=66_421.35,
            market_value=16_470,
            allocation_percent=5.0,
            risk_level="high",
            beginner_explanation="Crypto can move sharply in price, so CrocLens treats it as higher risk.",
            source=MOCK_SOURCE,
        ),
        AssetResponse(
            id="asset_cash",
            symbol="USD",
            name="Cash reserve",
            asset_type="Cash",
            current_price=None,
            market_value=23_058,
            allocation_percent=7.0,
            risk_level="low",
            beginner_explanation="Cash is usually stable and liquid, but inflation can reduce buying power.",
            source=MOCK_SOURCE,
        ),
    ]


def get_asset_by_id(asset_id: str) -> AssetResponse | None:
    return next((asset for asset in list_assets() if asset.id == asset_id), None)


def get_action_plan() -> ActionPlanResponse:
    return ActionPlanResponse(
        plan_id="plan_mock_phase_3",
        items=[
            ActionPlanItem(
                id="action_cash_buffer",
                title="Review emergency cash target",
                description="Consider comparing your cash reserve with three months of core expenses.",
                priority="high",
                status="suggested",
                safe_wording_note="Uses review language, not a direct instruction.",
            ),
            ActionPlanItem(
                id="action_debt_rates",
                title="Compare debt interest rates",
                description="You may want to research whether high-interest debt is affecting net worth growth.",
                priority="medium",
                status="suggested",
                safe_wording_note="Frames the item as research, not advice.",
            ),
        ],
        confidence="medium",
        data_limitations=["Uses static sample data only.", "No live account or market data is connected."],
        educational_disclaimer=EDUCATIONAL_DISCLAIMER,
    )


def generate_action_plan() -> ActionPlanResponse:
    return get_action_plan()
