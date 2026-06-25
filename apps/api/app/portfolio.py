from app.schemas import DemoHolding, DemoPortfolioResponse


DEMO_HOLDINGS = [
    {
        "symbol": "VTI",
        "name": "Vanguard Total Stock Market ETF",
        "quantity": 6,
        "latest_price": 305.25,
        "note": "Broad U.S. stock market exposure.",
    },
    {
        "symbol": "VXUS",
        "name": "Vanguard Total International Stock ETF",
        "quantity": 8,
        "latest_price": 66.4,
        "note": "International stock diversification.",
    },
    {
        "symbol": "BND",
        "name": "Vanguard Total Bond Market ETF",
        "quantity": 5,
        "latest_price": 73.1,
        "note": "Bond exposure can reduce all-stock concentration.",
    },
]


async def get_demo_portfolio() -> DemoPortfolioResponse:
    rows = []
    total = sum(item["quantity"] * item["latest_price"] for item in DEMO_HOLDINGS)
    for item in DEMO_HOLDINGS:
        value = item["quantity"] * item["latest_price"]
        rows.append(
            DemoHolding(
                symbol=item["symbol"],
                name=item["name"],
                quantity=item["quantity"],
                latest_price=item["latest_price"],
                market_value=round(value, 2),
                allocation_percent=round((value / total) * 100, 1),
                note=item["note"],
            )
        )

    return DemoPortfolioResponse(holdings=rows, total_value=round(total, 2))
