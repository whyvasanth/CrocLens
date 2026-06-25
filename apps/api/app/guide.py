from app.schemas import GuideResponse, QuoteResponse


def explain_quote(quote: QuoteResponse) -> GuideResponse:
    observations: list[str] = []
    considerations: list[str] = [
        "Look at more than one day of movement before forming an opinion.",
        "Compare this asset with the rest of a portfolio instead of viewing it alone.",
        "Use this as a starting point for research, not as a trading instruction.",
    ]

    if quote.change_percent is None:
        movement = "CrocLens could not calculate the recent price movement from the available data."
    elif quote.change_percent > 1:
        movement = f"{quote.symbol} moved up about {quote.change_percent:.2f}% versus the previous close."
    elif quote.change_percent < -1:
        movement = f"{quote.symbol} moved down about {abs(quote.change_percent):.2f}% versus the previous close."
    else:
        movement = f"{quote.symbol} was relatively flat versus the previous close."

    observations.append(movement)

    if quote.day_high and quote.day_low and quote.price:
        daily_range = ((quote.day_high - quote.day_low) / quote.price) * 100
        observations.append(
            f"The daily high-low range is about {daily_range:.2f}% of the latest price, a simple volatility clue."
        )

    if quote.market_cap:
        observations.append("Market cap gives a rough sense of company size, but it does not measure quality by itself.")

    return GuideResponse(
        symbol=quote.symbol,
        summary=f"{quote.name} is trading at the latest available yfinance price of {quote.price:.2f} {quote.currency}.",
        observations=observations,
        considerations=considerations,
        data_limitations=quote.data_limitations,
    )
