from statistics import mean

from app.data_providers.base import BaseDataProvider, utc_now
from app.data_providers.schemas import PriceHistoryResponse, TechnicalIndicator, TechnicalIndicatorResponse


class StockstatsProvider(BaseDataProvider):
    provider_id = "stockstats"
    display_name = "stockstats indicators"
    source_type = "derived_indicator_library"
    capabilities = ["technical_indicators"]
    requires_api_key = False
    cost_note = "Free open-source Python library; derives indicators from OHLCV data."
    limitations = [
        "Technical indicators are educational context, not trading instructions.",
        "Indicator quality depends on the completeness and freshness of the underlying OHLCV data.",
    ]

    def get_technical_indicators(self, history: PriceHistoryResponse) -> TechnicalIndicatorResponse:
        closes = [point.close for point in history.points if point.close is not None]
        if not closes:
            indicators = [
                TechnicalIndicator(
                    name="data_status",
                    value=None,
                    explanation="No close prices were available to calculate indicators.",
                )
            ]
        else:
            indicators = [
                TechnicalIndicator(
                    name="latest_close",
                    value=round(closes[-1], 4),
                    explanation="Most recent close in the normalized OHLCV series.",
                ),
                TechnicalIndicator(
                    name="sma_20",
                    value=round(mean(closes[-20:]), 4) if len(closes) >= 20 else None,
                    explanation="Simple 20-period average. It smooths price movement but should not be used alone.",
                ),
                TechnicalIndicator(
                    name="rsi_14",
                    value=_calculate_rsi(closes[-15:]) if len(closes) >= 15 else None,
                    explanation="Approximate 14-period RSI. It can highlight momentum, but it is not a buy/sell signal.",
                ),
            ]

        return TechnicalIndicatorResponse(
            provider=self.provider_id,
            asset_type=history.asset_type,
            symbol_or_series_id=history.symbol_or_series_id,
            as_of=history.as_of,
            retrieved_at=utc_now(),
            freshness=f"Derived from {history.provider} data as of {history.as_of.date().isoformat()}",
            confidence="medium" if closes else "low",
            limitations=self.limitations + history.limitations,
            indicators=indicators,
            source_url=history.source_url,
            fallback_chain=history.fallback_chain,
        )


def _calculate_rsi(closes: list[float]) -> float | None:
    gains: list[float] = []
    losses: list[float] = []
    for previous, current in zip(closes, closes[1:]):
        change = current - previous
        if change >= 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))

    average_gain = mean(gains)
    average_loss = mean(losses)
    if average_loss == 0:
        return 100.0

    rs = average_gain / average_loss
    return round(100 - (100 / (1 + rs)), 2)
