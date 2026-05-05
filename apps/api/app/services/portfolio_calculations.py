from dataclasses import dataclass
from collections import defaultdict

from app.schemas.api import AllocationItem, DebtImpact, ScoreItem


@dataclass(frozen=True)
class AssetPosition:
    asset_class: str
    market_value: float


@dataclass(frozen=True)
class LiabilityPosition:
    liability_type: str
    balance: float
    interest_rate: float | None = None


@dataclass(frozen=True)
class PortfolioCalculationResult:
    total_assets: float
    total_liabilities: float
    net_worth: float
    allocation: list[AllocationItem]
    debt_impact: DebtImpact
    scores: list[ScoreItem]


RISK_WEIGHTS = {
    "Stocks": 70,
    "ETFs": 55,
    "Mutual Funds": 55,
    "Crypto": 95,
    "Real Estate": 65,
    "Cash": 10,
    "Bonds": 30,
    "Treasuries": 20,
    "Retirement": 55,
}

LIQUIDITY_WEIGHTS = {
    "Stocks": 85,
    "ETFs": 85,
    "Mutual Funds": 75,
    "Crypto": 70,
    "Real Estate": 15,
    "Cash": 100,
    "Bonds": 65,
    "Treasuries": 80,
    "Retirement": 35,
}

INCOME_YIELD_WEIGHTS = {
    "Stocks": 35,
    "ETFs": 45,
    "Mutual Funds": 45,
    "Crypto": 5,
    "Real Estate": 55,
    "Cash": 25,
    "Bonds": 75,
    "Treasuries": 70,
    "Retirement": 45,
}

INFLATION_RESILIENCE_WEIGHTS = {
    "Stocks": 65,
    "ETFs": 60,
    "Mutual Funds": 60,
    "Crypto": 35,
    "Real Estate": 75,
    "Cash": 20,
    "Bonds": 45,
    "Treasuries": 35,
    "Retirement": 60,
}

TAX_COMPLEXITY_WEIGHTS = {
    "Stocks": 55,
    "ETFs": 40,
    "Mutual Funds": 55,
    "Crypto": 85,
    "Real Estate": 80,
    "Cash": 10,
    "Bonds": 50,
    "Treasuries": 35,
    "Retirement": 30,
}


def clamp_score(value: float) -> int:
    return max(0, min(100, round(value)))


def calculate_totals(
    assets: list[AssetPosition],
    liabilities: list[LiabilityPosition],
) -> tuple[float, float, float]:
    total_assets = round(sum(asset.market_value for asset in assets), 2)
    total_liabilities = round(sum(liability.balance for liability in liabilities), 2)
    return total_assets, total_liabilities, round(total_assets - total_liabilities, 2)


def calculate_allocation(assets: list[AssetPosition], total_assets: float) -> list[AllocationItem]:
    by_class: dict[str, float] = defaultdict(float)
    for asset in assets:
        by_class[asset.asset_class] += asset.market_value

    if total_assets <= 0:
        return []

    return [
        AllocationItem(
            asset_class=asset_class,
            market_value=round(market_value, 2),
            percent=round((market_value / total_assets) * 100, 2),
        )
        for asset_class, market_value in sorted(by_class.items(), key=lambda item: item[1], reverse=True)
    ]


def calculate_debt_impact(total_assets: float, liabilities: list[LiabilityPosition]) -> DebtImpact:
    total_liabilities = round(sum(liability.balance for liability in liabilities), 2)
    debt_to_asset_percent = 0 if total_assets <= 0 else round((total_liabilities / total_assets) * 100, 2)

    if debt_to_asset_percent >= 50:
        explanation = "Liabilities are a large share of tracked assets, so debt can strongly affect net worth."
    elif debt_to_asset_percent >= 25:
        explanation = "Liabilities are meaningful but not larger than tracked assets."
    else:
        explanation = "Liabilities are a smaller share of tracked assets based on the data provided."

    return DebtImpact(
        debt_to_asset_percent=debt_to_asset_percent,
        total_liabilities=total_liabilities,
        explanation=explanation,
    )


def weighted_asset_score(
    assets: list[AssetPosition],
    weights: dict[str, int],
    default_weight: int,
) -> int:
    total_assets = sum(asset.market_value for asset in assets)
    if total_assets <= 0:
        return 0

    weighted_total = sum(
        asset.market_value * weights.get(asset.asset_class, default_weight)
        for asset in assets
    )
    return clamp_score(weighted_total / total_assets)


def calculate_diversification_score(allocation: list[AllocationItem]) -> int:
    if not allocation:
        return 0

    asset_class_count = len(allocation)
    largest_percent = max(item.percent for item in allocation)
    count_bonus = min(asset_class_count, 6) * 8
    concentration_penalty = max(0, largest_percent - 35) * 1.2
    return clamp_score(40 + count_bonus - concentration_penalty)


def calculate_scores(assets: list[AssetPosition], allocation: list[AllocationItem]) -> list[ScoreItem]:
    return [
        ScoreItem(
            label="Risk",
            value=weighted_asset_score(assets, RISK_WEIGHTS, default_weight=60),
            explanation="Market-value-weighted estimate of how volatile the asset mix may be.",
            formula="sum(asset market value * asset-class risk weight) / total assets",
        ),
        ScoreItem(
            label="Liquidity",
            value=weighted_asset_score(assets, LIQUIDITY_WEIGHTS, default_weight=50),
            explanation="Higher means more of the portfolio is in assets that are usually easier to access or sell.",
            formula="sum(asset market value * asset-class liquidity weight) / total assets",
        ),
        ScoreItem(
            label="Diversification",
            value=calculate_diversification_score(allocation),
            explanation="Rewards having more asset classes and penalizes a very large concentration in one class.",
            formula="40 + min(asset class count, 6) * 8 - concentration penalty",
        ),
        ScoreItem(
            label="Income/yield",
            value=weighted_asset_score(assets, INCOME_YIELD_WEIGHTS, default_weight=35),
            explanation="Higher means the asset mix may produce more interest, dividends, rent, or yield.",
            formula="sum(asset market value * asset-class income weight) / total assets",
        ),
        ScoreItem(
            label="Inflation resilience",
            value=weighted_asset_score(assets, INFLATION_RESILIENCE_WEIGHTS, default_weight=50),
            explanation="Higher means the asset mix may be less exposed to inflation eroding purchasing power.",
            formula="sum(asset market value * asset-class inflation-resilience weight) / total assets",
        ),
        ScoreItem(
            label="Tax complexity",
            value=weighted_asset_score(assets, TAX_COMPLEXITY_WEIGHTS, default_weight=50),
            explanation="Higher means the mix may need more tax tracking, such as lots, income, or property records.",
            formula="sum(asset market value * asset-class tax-complexity weight) / total assets",
        ),
    ]


def calculate_portfolio_summary(
    assets: list[AssetPosition],
    liabilities: list[LiabilityPosition],
) -> PortfolioCalculationResult:
    total_assets, total_liabilities, net_worth = calculate_totals(assets, liabilities)
    allocation = calculate_allocation(assets, total_assets)

    return PortfolioCalculationResult(
        total_assets=total_assets,
        total_liabilities=total_liabilities,
        net_worth=net_worth,
        allocation=allocation,
        debt_impact=calculate_debt_impact(total_assets, liabilities),
        scores=calculate_scores(assets, allocation),
    )
