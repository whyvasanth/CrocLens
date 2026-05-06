from app.schemas.api import SourceMetadata, WatchlistCreateRequest, WatchlistItemResponse, WatchlistResponse
from app.services.mock_data import EDUCATIONAL_DISCLAIMER


WATCHLIST_SOURCE = SourceMetadata(
    name="CrocLens sample watchlist",
    freshness="Sample watchlist intelligence",
    as_of="2026-05-06",
)


def get_watchlist() -> WatchlistResponse:
    items = [
        WatchlistItemResponse(
            id="watch_vti",
            symbol="VTI",
            name="Vanguard Total Stock Market ETF",
            asset_type="etf",
            why_watching="Researching a broad ETF as a simple diversified building block.",
            ai_summary="Broad-market ETFs can be beginner-friendly, but overlap, taxes, and time horizon still matter.",
            risk_notes=[
                "Still exposed to stock market downturns.",
                "ETF overlap can make diversification look stronger than it is.",
            ],
            opportunity_notes=[
                "May provide broad diversification in one fund.",
                "Can be easier to understand than many individual stocks.",
            ],
            source=WATCHLIST_SOURCE,
            confidence="medium",
            data_limitations=["Sample watchlist item only.", "No live fund data or holdings feed is connected."],
        ),
        WatchlistItemResponse(
            id="watch_us10y",
            symbol="US10Y",
            name="10Y Treasury yield",
            asset_type="treasury",
            why_watching="Learning how rates affect bonds, mortgages, cash, and stock valuations.",
            ai_summary="Treasury yields can influence several parts of a financial life, not only bonds.",
            risk_notes=[
                "Rate headlines can be noisy in the short term.",
                "Yield changes do not affect every asset in the same way.",
            ],
            opportunity_notes=[
                "Useful context for mortgage and bond decisions.",
                "Helps beginners compare cash yield with inflation.",
            ],
            source=WATCHLIST_SOURCE,
            confidence="medium",
            data_limitations=["Sample rate context only.", "No official Treasury API is connected yet."],
        ),
    ]

    return WatchlistResponse(
        items=items,
        beginner_summary="A watchlist is a research queue. It helps you track what to learn next without treating the list as a buy list.",
        safe_research_prompts=[
            "Why am I watching this?",
            "What risk would make this unsuitable for my goal?",
            "What source would I check before making a real decision?",
        ],
        confidence="medium",
        data_limitations=[
            "Uses sample watchlist entries only.",
            "No live prices, ratings, analyst data, or paid providers are connected.",
            "AI summaries are rule-based educational notes.",
        ],
        sources=[WATCHLIST_SOURCE],
        educational_disclaimer=EDUCATIONAL_DISCLAIMER,
    )


def create_watchlist_item(request: WatchlistCreateRequest) -> WatchlistItemResponse:
    symbol = request.symbol.upper()

    return WatchlistItemResponse(
        id=f"watch_preview_{symbol.lower()}",
        symbol=symbol,
        name=request.name,
        asset_type=request.asset_type,
        why_watching=request.why_watching,
        ai_summary=(
            "CrocLens would track this as a research item. Consider comparing the reason you are watching it "
            "with risk, time horizon, liquidity, and taxes before making any decision."
        ),
        risk_notes=[
            "The watchlist does not mean this asset is appropriate.",
            "Review data freshness and source quality before relying on any metric.",
        ],
        opportunity_notes=[
            "A clear watch reason can make research more focused.",
            "Comparing this item with your full financial picture can prevent narrow decisions.",
        ],
        source=WATCHLIST_SOURCE,
        confidence="medium",
        data_limitations=["Preview response only.", "The item is not persisted until database-backed storage is added."],
    )
