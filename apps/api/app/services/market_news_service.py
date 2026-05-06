from app.schemas.api import (
    HoldingImpactResponse,
    MarketNewsImpactResponse,
    NewsArticleResponse,
    SourceMetadata,
)
from app.services.mock_data import EDUCATIONAL_DISCLAIMER, MOCK_SOURCE, list_assets


NEWS_SOURCE = SourceMetadata(
    name="CrocLens sample news",
    freshness="Sample educational news context",
    as_of="2026-05-06",
)


def get_market_news_impact() -> MarketNewsImpactResponse:
    articles = [
        NewsArticleResponse(
            id="news_rates_hold",
            title="Treasury yields remain elevated in sample market context",
            source_name="CrocLens sample news",
            published_at="2026-05-06T09:30:00-04:00",
            summary=(
                "Higher yields can affect bond prices, mortgage affordability, and how investors compare cash, "
                "bonds, and stocks."
            ),
            topic="rates",
            affected_asset_classes=["Bonds", "Real Estate", "Cash", "Stocks"],
            confidence="medium",
            data_limitations=["Sample article only.", "No live news feed is connected."],
        ),
        NewsArticleResponse(
            id="news_tech_volatility",
            title="Technology shares show higher short-term volatility",
            source_name="CrocLens sample news",
            published_at="2026-05-06T10:15:00-04:00",
            summary=(
                "Technology-heavy holdings may move more than broad diversified funds during volatile market days."
            ),
            topic="equities",
            affected_asset_classes=["Stocks", "ETFs", "Retirement"],
            confidence="medium",
            data_limitations=["Sample article only.", "Sector-level exposure is estimated from mock holdings."],
        ),
    ]

    affected_holdings = _map_articles_to_holdings()

    return MarketNewsImpactResponse(
        headline="Rate and stock volatility headlines mainly touch your stocks, ETFs, real estate, and retirement mix.",
        beginner_summary=(
            "CrocLens is not saying to buy or sell. It is showing which parts of the sample portfolio may be worth "
            "reviewing when rates or stock volatility are in the news."
        ),
        portfolio_exposure_summary=(
            "The sample portfolio has meaningful stock and ETF exposure, a real estate position, retirement assets, "
            "cash, and mortgage debt. That means rates and broad stock moves can affect several areas at once."
        ),
        articles=articles,
        affected_holdings=affected_holdings,
        suggested_questions=[
            "Which holdings are most sensitive to interest rates?",
            "Is my stock exposure diversified enough for my time horizon?",
            "Do I have enough cash flexibility if rates stay elevated?",
        ],
        confidence="medium",
        data_limitations=[
            "Uses sample news and sample holdings only.",
            "Does not use live news, brokerage data, or real-time prices.",
            "Impact language is educational and should not be treated as financial advice.",
        ],
        sources=[NEWS_SOURCE, MOCK_SOURCE],
        educational_disclaimer=EDUCATIONAL_DISCLAIMER,
    )


def _map_articles_to_holdings() -> list[HoldingImpactResponse]:
    impacts: list[HoldingImpactResponse] = []

    for asset in list_assets():
        asset_type = asset.asset_type.lower()
        if asset_type in {"stocks", "etfs", "retirement"}:
            impacts.append(
                HoldingImpactResponse(
                    holding_id=asset.id,
                    symbol=asset.symbol,
                    name=asset.name,
                    asset_type=asset.asset_type,
                    impact_direction="mixed",
                    impact_level="medium",
                    why_it_matters="Stock and fund values can react to rate expectations, earnings news, and volatility.",
                    what_to_watch=[
                        "Whether one sector drives too much of the portfolio movement.",
                        "How short-term volatility compares with the user's time horizon.",
                    ],
                )
            )
        elif asset_type == "real estate":
            impacts.append(
                HoldingImpactResponse(
                    holding_id=asset.id,
                    symbol=asset.symbol,
                    name=asset.name,
                    asset_type=asset.asset_type,
                    impact_direction="mixed",
                    impact_level="medium",
                    why_it_matters="Rates can affect mortgage costs, buyer demand, and real estate affordability.",
                    what_to_watch=[
                        "Mortgage rate assumptions before refinancing or buying.",
                        "Local housing trends instead of national headlines alone.",
                    ],
                )
            )
        elif asset_type == "cash":
            impacts.append(
                HoldingImpactResponse(
                    holding_id=asset.id,
                    symbol=asset.symbol,
                    name=asset.name,
                    asset_type=asset.asset_type,
                    impact_direction="neutral",
                    impact_level="low",
                    why_it_matters="Cash can provide flexibility when markets move, but inflation can reduce buying power.",
                    what_to_watch=[
                        "Emergency fund coverage.",
                        "Whether cash yield is keeping up with inflation.",
                    ],
                )
            )

    return impacts
