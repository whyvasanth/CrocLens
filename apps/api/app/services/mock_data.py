from app.schemas.api import (
    ActionPlanItem,
    ActionPlanResponse,
    AllocationItem,
    AssetResponse,
    PortfolioSummaryResponse,
    ScoreItem,
    SourceMetadata,
)

MOCK_SOURCE = SourceMetadata(
    name="CrocLens sample data",
    freshness="Static mock data for Phase 3",
    as_of="2026-05-05",
)

EDUCATIONAL_DISCLAIMER = "This is educational information, not financial advice."


def get_portfolio_summary() -> PortfolioSummaryResponse:
    total_assets = 329_400.0
    total_liabilities = 114_600.0

    return PortfolioSummaryResponse(
        user_name="Maya",
        total_assets=total_assets,
        total_liabilities=total_liabilities,
        net_worth=total_assets - total_liabilities,
        allocation=[
            AllocationItem(asset_class="Stocks", percent=29, market_value=95_526),
            AllocationItem(asset_class="ETFs", percent=24, market_value=79_056),
            AllocationItem(asset_class="Real Estate", percent=22, market_value=72_468),
            AllocationItem(asset_class="Retirement", percent=13, market_value=42_822),
            AllocationItem(asset_class="Cash", percent=7, market_value=23_058),
            AllocationItem(asset_class="Crypto", percent=5, market_value=16_470),
        ],
        scores=[
            ScoreItem(
                label="Risk",
                value=64,
                explanation="Moderate because stocks and crypto move more than cash or bonds.",
            ),
            ScoreItem(
                label="Liquidity",
                value=72,
                explanation="Healthy because cash and tradable funds are available if needed.",
            ),
            ScoreItem(
                label="Diversification",
                value=78,
                explanation="Good mix across public markets, cash, and real estate.",
            ),
        ],
        sources=[MOCK_SOURCE],
        educational_disclaimer=EDUCATIONAL_DISCLAIMER,
    )


def list_assets() -> list[AssetResponse]:
    return [
        AssetResponse(
            id="asset_voo",
            symbol="VOO",
            name="Vanguard S&P 500 ETF",
            asset_type="ETF",
            current_price=486.20,
            market_value=44_200,
            allocation_percent=13.4,
            risk_level="medium",
            beginner_explanation="An ETF is a basket of investments. This one tracks large U.S. companies.",
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

