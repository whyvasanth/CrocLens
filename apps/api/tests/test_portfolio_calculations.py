from app.services.portfolio_calculations import (
    AssetPosition,
    LiabilityPosition,
    calculate_allocation,
    calculate_debt_impact,
    calculate_portfolio_summary,
    calculate_totals,
)


SAMPLE_ASSETS = [
    AssetPosition(asset_class="Stocks", market_value=95_526),
    AssetPosition(asset_class="ETFs", market_value=79_056),
    AssetPosition(asset_class="Real Estate", market_value=72_468),
    AssetPosition(asset_class="Retirement", market_value=42_822),
    AssetPosition(asset_class="Cash", market_value=23_058),
    AssetPosition(asset_class="Crypto", market_value=16_470),
]

SAMPLE_LIABILITIES = [
    LiabilityPosition(liability_type="Mortgage", balance=106_000, interest_rate=0.061),
    LiabilityPosition(liability_type="Student loan", balance=6_100, interest_rate=0.045),
    LiabilityPosition(liability_type="Credit card", balance=2_500, interest_rate=0.199),
]


def test_calculate_totals() -> None:
    total_assets, total_liabilities, net_worth = calculate_totals(SAMPLE_ASSETS, SAMPLE_LIABILITIES)

    assert total_assets == 329_400
    assert total_liabilities == 114_600
    assert net_worth == 214_800


def test_calculate_allocation() -> None:
    allocation = calculate_allocation(SAMPLE_ASSETS, total_assets=329_400)

    assert allocation[0].asset_class == "Stocks"
    assert allocation[0].percent == 29
    assert sum(item.percent for item in allocation) == 100


def test_calculate_debt_impact() -> None:
    debt_impact = calculate_debt_impact(total_assets=329_400, liabilities=SAMPLE_LIABILITIES)

    assert debt_impact.total_liabilities == 114_600
    assert debt_impact.debt_to_asset_percent == 34.79
    assert "meaningful" in debt_impact.explanation


def test_calculate_portfolio_summary_scores_are_auditable() -> None:
    summary = calculate_portfolio_summary(SAMPLE_ASSETS, SAMPLE_LIABILITIES)
    scores = {score.label: score for score in summary.scores}

    assert set(scores) == {
        "Risk",
        "Liquidity",
        "Diversification",
        "Income/yield",
        "Inflation resilience",
        "Tax complexity",
    }
    assert scores["Risk"].formula
    assert scores["Diversification"].value == 88
    assert all(0 <= score.value <= 100 for score in summary.scores)

